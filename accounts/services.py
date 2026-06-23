"""
accounts/services.py
Service layer untuk modul Autentikasi & Manajemen Admin.

Tanggung jawab:
- Verifikasi session (baca profil admin dari Firestore setelah verifikasi token)
- Kelola akun admin (buat, update role, nonaktifkan) via Firebase Auth & Firestore
- Agregasi data untuk dashboard summary

Collection Firestore: "admin_profiles"
Firebase Auth: Custom Claims untuk `role`
"""

import logging
from datetime import datetime, timezone

from firebase_admin import auth as firebase_auth

from core.firebase_client import db
from berita.services import BeritaService
from proker.services import ProkerService
from pengaduan.services import PengaduanService

logger = logging.getLogger(__name__)

COLLECTION = "admin_profiles"
ROLE_SUPER_ADMIN = "super_admin"
ROLE_EDITOR = "editor"
VALID_ROLES = {ROLE_SUPER_ADMIN, ROLE_EDITOR}


def _doc_to_dict(doc) -> dict:
    d = doc.to_dict() or {}
    d["uid"] = doc.id
    return d


class AccountsService:

    @staticmethod
    def get_session_profile(uid: str) -> dict | None:
        """
        Ambil profil admin dari Firestore berdasarkan UID.
        Dipanggil oleh POST /api/auth/session setelah token terverifikasi.
        """
        doc = db.collection(COLLECTION).document(uid).get()
        if not doc.exists:
            return None
        return _doc_to_dict(doc)

    @staticmethod
    def list_admins(page: int = 1, limit: int = 20) -> dict:
        """Daftar semua akun admin."""
        all_docs = list(db.collection(COLLECTION).order_by("nama").stream())
        total = len(all_docs)
        offset = (page - 1) * limit
        paged = all_docs[offset: offset + limit]
        return {
            "results": [_doc_to_dict(d) for d in paged],
            "meta": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": (total + limit - 1) // limit if total > 0 else 1,
            },
        }

    @staticmethod
    def create_admin(email: str, password: str, nama: str, role: str) -> dict:
        """
        Buat akun admin baru:
        1. Buat user di Firebase Auth
        2. Set custom claim `role`
        3. Simpan profil ke Firestore admin_profiles (doc ID = UID)

        Raises:
            ValueError: jika role tidak valid atau email sudah terdaftar
        """
        if role not in VALID_ROLES:
            raise ValueError(f"Role tidak valid. Pilihan: {', '.join(sorted(VALID_ROLES))}")

        try:
            firebase_user = firebase_auth.create_user(
                email=email,
                password=password,
                display_name=nama,
            )
        except firebase_auth.EmailAlreadyExistsError:
            raise ValueError("Email sudah terdaftar sebagai akun admin.")
        except Exception as e:
            raise ValueError(f"Gagal membuat akun Firebase: {e}")

        # Set custom claim role
        firebase_auth.set_custom_user_claims(firebase_user.uid, {"role": role})

        # Simpan profil ke Firestore
        now = datetime.now(timezone.utc)
        profile_data = {
            "nama": nama,
            "email": email,
            "role": role,
            "status_aktif": True,
            "created_at": now,
            "updated_at": now,
        }
        db.collection(COLLECTION).document(firebase_user.uid).set(profile_data)

        return {"uid": firebase_user.uid, **profile_data}

    @staticmethod
    def update_admin(uid: str, data: dict) -> dict | None:
        """
        Update profil admin (nama, role, status_aktif).
        Returns None jika UID tidak ditemukan.
        Raises: ValueError jika role tidak valid
        """
        ref = db.collection(COLLECTION).document(uid)
        if not ref.get().exists:
            return None

        # Update role di Firebase Auth custom claims jika berubah
        if "role" in data:
            if data["role"] not in VALID_ROLES:
                raise ValueError(f"Role tidak valid. Pilihan: {', '.join(sorted(VALID_ROLES))}")
            firebase_auth.set_custom_user_claims(uid, {"role": data["role"]})

        # Nonaktifkan akun di Firebase Auth jika status_aktif = False
        if "status_aktif" in data:
            try:
                firebase_auth.update_user(uid, disabled=not data["status_aktif"])
            except Exception as e:
                logger.warning("Gagal update disabled status di Firebase Auth: %s", e)

        data["updated_at"] = datetime.now(timezone.utc)
        ref.update(data)
        return _doc_to_dict(ref.get())

    @staticmethod
    def get_dashboard_summary() -> dict:
        """
        Ringkasan untuk halaman dashboard admin:
        - Total berita terpublikasi
        - Total proker yang sedang berlangsung
        - Total pengaduan dengan status 'diterima' (belum diproses)
        """
        return {
            "total_berita_published": BeritaService.count_published(),
            "total_proker_aktif": ProkerService.count_active(),
            "total_pengaduan_masuk": PengaduanService.count_incoming(),
        }
