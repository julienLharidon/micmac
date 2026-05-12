#!/usr/bin/env python3
import os
import sys

# Ajouter le répertoire courant au path pour trouver pymicmac
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from pymicmac.cli.tapioca import main  # noqa: E402

if __name__ == "__main__":
    main()
