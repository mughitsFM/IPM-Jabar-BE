#!/usr/bin/env python
"""
scripts/create_superadmin.py
Script sekali jalan untuk membuat akun Super Admin pertama.

Cara pakai (dari folder backend/):
    python scripts/create_superadmin.py

Atau dengan env var:
    DJANGO_SETTINGS_MODULE=config.settings.dev python scripts/create_superadmin.py

Pastikan .env sudah terisi dan firebase-service-account.json tersedia.
"""

import os
import sys
import django

# Tambahkan root project ke path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
django.setup()


def main():
    from accounts.services import AccountsService

    print("=" * 55)
    print("  Setup Super Admin — PW IPM Jawa Barat")
    print("=" * 55)
    print()

    email = input("Email Super Admin  : ").strip()
    nama = input("Nama Lengkap       : ").strip()

    import getpass
    password = getpass.getpass("Password (min 8 karakter): ").strip()
    if len(password) < 8:
        print("\n[ERROR] Password minimal 8 karakter.")
        sys.exit(1)

    print()
    print(f"Membuat akun Super Admin untuk: {nama} <{email}>")
    konfirmasi = input("Lanjutkan? (y/n): ").strip().lower()

    if konfirmasi != "y":
        print("Dibatalkan.")
        sys.exit(0)

    try:
        profile = AccountsService.create_admin(
            email=email,
            password=password,
            nama=nama,
            role="super_admin",
        )
        print()
        print("[SUKSES] Akun Super Admin berhasil dibuat!")
        print(f"  UID   : {profile['uid']}")
        print(f"  Email : {profile['email']}")
        print(f"  Nama  : {profile['nama']}")
        print(f"  Role  : {profile['role']}")
        print()
        print("Gunakan email & password di atas untuk login ke panel admin.")
    except ValueError as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Terjadi kesalahan tak terduga: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
