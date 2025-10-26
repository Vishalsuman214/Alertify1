#!/usr/bin/env python3

import sys
import os

# Add the current directory to the path so we can import api modules
sys.path.insert(0, os.path.dirname(__file__))

try:
    from api.mongo_handler import get_client
    client = get_client()
    print("✅ MongoDB connection successful!")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    sys.exit(1)
