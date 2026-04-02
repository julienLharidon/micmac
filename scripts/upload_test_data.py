import argparse
from google.cloud import storage
import os

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)
    print(f"File {source_file_name} uploaded to {destination_blob_name}.")

def main():
    parser = argparse.ArgumentParser(description="Upload test data to GCS")
    parser.add_argument("--bucket", required=True, help="Target GCS bucket name")
    parser.add_argument("--dir", required=True, help="Source directory with images")
    args = parser.parse_args()

    for filename in os.listdir(args.dir):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.tif')):
            source = os.path.join(args.dir, filename)
            dest = f"raw-images/{filename}"
            upload_blob(args.bucket, source, dest)

if __name__ == "__main__":
    main()
