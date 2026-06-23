#!/usr/bin/env python
"""
scripts/check_firebase.py
Script diagnosa untuk memastikan koneksi ke Firebase berjalan normal.

Cara pakai:
    python scripts/check_firebase.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

import django
django.setup()


def check_firestore():
    print("1. Cek koneksi Firestore...", end=" ")
    try:
        from core.firebase_client import db
        # Coba baca satu dokumen (tidak ada isinya, hanya ping)
        list(db.collection("_health_check").limit(1).stream())
        print("OK ✓")
        return True
    except Exception as e:
        print(f"GAGAL ✗\n   → {e}")
        return False


def check_cloudinary():
    print("2. Cek koneksi Cloudinary...", end=" ")
    try:
        import cloudinary.api
        from django.conf import settings
        if not settings.CLOUDINARY_CLOUD_NAME:
            print("GAGAL ✗\n   → CLOUDINARY_CLOUD_NAME belum diisi di .env")
            return False
        # Ping Cloudinary API: ambil usage info (ringan, tidak ada upload)
        usage = cloudinary.api.usage()
        storage_used_mb = round(usage.get("storage", {}).get("used", 0) / (1024 ** 2), 2)
        print(f"OK ✓  (cloud: {settings.CLOUDINARY_CLOUD_NAME}, storage terpakai: {storage_used_mb} MB)")
        return True
    except Exception as e:
        print(f"GAGAL ✗\n   → {e}")
        return False


def check_auth():
    print("3. Cek Firebase Auth...", end=" ")
    try:
        from core.firebase_client import auth
        # List 1 user sebagai ping — tidak ada user pun tidak error
        auth.list_users(max_results=1)
        print("OK ✓")
        return True
    except Exception as e:
        print(f"GAGAL ✗\n   → {e}")
        return False


def main():
    print()
    print("=" * 55)
    print("  Connectivity Check — Firebase & Cloudinary")
    print("=" * 55)
    print()

    results = [check_firestore(), check_cloudinary(), check_auth()]

    print()
    if all(results):
        print("Semua layanan dapat dijangkau. Siap development!")
    else:
        print("Ada layanan yang gagal dijangkau. Periksa:")
        print("  • FIREBASE_SERVICE_ACCOUNT_PATH di .env")
        print("  • CLOUDINARY_CLOUD_NAME / API_KEY / API_SECRET di .env")
        print("  • Koneksi internet / firewall")
        sys.exit(1)


if __name__ == "__main__":
    main()
