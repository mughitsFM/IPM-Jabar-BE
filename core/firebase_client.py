"""
core/firebase_client.py
Inisialisasi Firebase Admin SDK satu kali di sini.
Expose `db` (Firestore) dan `auth` (Firebase Auth).

Catatan: Firebase Storage TIDAK digunakan lagi.
File upload ditangani Cloudinary (lihat storage_files/services.py).

Diimpor oleh:
- core/authentication.py → verifikasi ID Token
- accounts/services.py   → set custom claims, kelola user Firebase Auth
- berita/services.py     → CRUD Firestore collection "berita"
- profil/services.py     → CRUD Firestore collection "profil_pengurus"
- proker/services.py     → CRUD Firestore collection "program_kerja"
- pengaduan/services.py  → CRUD Firestore collection "pengaduan"
"""

import firebase_admin
from firebase_admin import credentials, firestore, auth as firebase_auth
from django.conf import settings


def _initialize_firebase() -> firebase_admin.App:
    """
    Inisialisasi Firebase Admin App.
    Jika sudah diinisialisasi sebelumnya (misal saat reload dev server),
    kembalikan app yang sudah ada.
    """
    try:
        return firebase_admin.get_app()
    except ValueError:
        cred = credentials.Certificate(settings.FIREBASE_SERVICE_ACCOUNT_PATH)
        # Tidak ada storageBucket — Storage sudah diganti Cloudinary
        return firebase_admin.initialize_app(cred)


_app = _initialize_firebase()

# ─── Shortcuts yang dipakai di seluruh project ────────────────────────────────
db: firestore.Client = firestore.client(_app)   # Firestore database client
auth = firebase_auth                             # Firebase Auth module

__all__ = ["db", "auth"]
