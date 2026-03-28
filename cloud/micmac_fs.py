#!/usr/bin/env python3
import os
import sys
import errno
import logging
import threading
import hashlib
from fuse import FUSE, FuseOSError, Operations
from google.cloud import storage
import redis

# Configuration (ENV variables)
BUCKET_NAME = os.getenv("GCS_BUCKET", "micmac-data")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
LOCAL_CACHE_DIR = os.getenv("MICMAC_LOCAL_CACHE", "/tmp/micmac_cache")

class MicMacCloudFS(Operations):
    def __init__(self, bucket_name, redis_client):
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(bucket_name)
        self.redis = redis_client
        self.local_cache = LOCAL_CACHE_DIR
        os.makedirs(self.local_cache, exist_ok=True)

        # In-memory Metadata Cache
        self._dir_cache = {}
        self._dirty_files = set()
        self._lock = threading.Lock()

    def _full_path(self, partial):
        if partial.startswith("/"):
            partial = partial[1:]
        return partial

    def _get_local_path(self, path):
        # Use a hash of the path to avoid collisions while keeping a flat local structure
        # or recreate the directory structure locally. Recreating structure is safer.
        full_path = self._full_path(path)
        local_path = os.path.join(self.local_cache, full_path)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        return local_path

    # --- Metadata ---
    def getattr(self, path, fh=None):
        full_path = self._full_path(path)
        if path == "/":
             return dict(st_mode=(16877), st_nlink=2, st_size=4096)

        # Check Local Cache First
        local_path = self._get_local_path(path)
        if os.path.exists(local_path):
            st = os.lstat(local_path)
            return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
                        'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))

        # Check GCS
        blob = self.bucket.get_blob(full_path)
        if blob:
             return dict(st_mode=(33188), st_nlink=1, st_size=blob.size)

        # Check if it's a virtual directory in GCS
        with self._lock:
            if full_path in self._dir_cache:
                return self._dir_cache[full_path]

            blobs = list(self.bucket.list_blobs(prefix=full_path + "/", max_results=1))
            if blobs:
                attr = dict(st_mode=(16877), st_nlink=2, st_size=4096)
                self._dir_cache[full_path] = attr
                return attr

        raise FuseOSError(errno.ENOENT)

    # --- Directory Operations ---
    def readdir(self, path, fh):
        full_path = self._full_path(path)
        dirents = ['.', '..']
        prefix = full_path + "/" if full_path else ""

        # GCS listing
        blobs = self.bucket.list_blobs(prefix=prefix, delimiter="/")
        for b in blobs:
            dirents.append(os.path.basename(b.name.rstrip("/")))
        for p in blobs.prefixes:
            dirents.append(os.path.basename(p.rstrip("/")))

        # Local listing
        local_dir = self._get_local_path(path)
        if os.path.isdir(local_dir):
            dirents.extend(os.listdir(local_dir))

        return list(set(dirents))

    def mkdir(self, path, mode):
        local_path = self._get_local_path(path)
        os.makedirs(local_path, exist_ok=True)
        with self._lock:
            self._dir_cache[self._full_path(path)] = dict(st_mode=(16877), st_nlink=2, st_size=4096)
        return 0

    # --- File Operations ---
    def create(self, path, mode, fi=None):
        local_path = self._get_local_path(path)
        self._dirty_files.add(path)
        return os.open(local_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, mode)

    def open(self, path, flags):
        full_path = self._full_path(path)
        local_path = self._get_local_path(path)

        if not os.path.exists(local_path):
            # 1. Try Redis first (for fast tie-point access)
            cached_data = self.redis.get(f"file:{full_path}")
            if cached_data:
                with open(local_path, "wb") as f:
                    f.write(cached_data)
            else:
                # 2. Try GCS
                blob = self.bucket.get_blob(full_path)
                if blob:
                    blob.download_to_filename(local_path)

        if (flags & os.O_WRONLY) or (flags & os.O_RDWR):
            self._dirty_files.add(path)

        return os.open(local_path, flags)

    def read(self, path, length, offset, fh):
        os.lseek(fh, offset, os.SEEK_SET)
        return os.read(fh, length)

    def write(self, path, data, offset, fh):
        os.lseek(fh, offset, os.SEEK_SET)
        written = os.write(fh, data)
        self._dirty_files.add(path)
        return written

    def truncate(self, path, length, fh=None):
        local_path = self._get_local_path(path)
        with open(local_path, 'r+') as f:
            f.truncate(length)
        self._dirty_files.add(path)

    def release(self, path, fh):
        os.close(fh)
        if path in self._dirty_files:
            full_path = self._full_path(path)
            local_path = self._get_local_path(path)

            # Upload to GCS
            blob = self.bucket.blob(full_path)
            blob.upload_from_filename(local_path)

            # Sync to Redis for "Homol" (Tie points)
            if "Homol" in full_path:
                with open(local_path, "rb") as f:
                    self.redis.set(f"file:{full_path}", f.read(), ex=3600) # 1h cache

            self._dirty_files.remove(path)
        return 0

    def unlink(self, path):
        full_path = self._full_path(path)
        local_path = self._get_local_path(path)
        if os.path.exists(local_path):
            os.remove(local_path)
        self.bucket.blob(full_path).delete()
        if path in self._dirty_files:
            self._dirty_files.remove(path)
        return 0

    def rename(self, old, new):
        old_full = self._full_path(old)
        new_full = self._full_path(new)

        # GCS Copy + Delete
        old_blob = self.bucket.blob(old_full)
        if old_blob.exists():
            self.bucket.copy_blob(old_blob, self.bucket, new_full)
            old_blob.delete()

        # Local Rename
        old_local = self._get_local_path(old)
        new_local = self._get_local_path(new)
        if os.path.exists(old_local):
            os.rename(old_local, new_local)
        return 0

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: %s <mountpoint>' % sys.argv[0])
        sys.exit(1)

    logging.basicConfig(level=logging.INFO)
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
    fuse = FUSE(MicMacCloudFS(BUCKET_NAME, r), sys.argv[1], foreground=True, allow_other=True)
