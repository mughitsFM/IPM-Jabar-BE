"""
profil/services.py
Service layer untuk modul Profil Kepengurusan.
Firestore collection: "profil_pengurus"
"""

from datetime import datetime, timezone
from core.firebase_client import db

COLLECTION = "profil_pengurus"


def _doc_to_dict(doc) -> dict:
    d = doc.to_dict() or {}
    d["id"] = doc.id
    return d


class ProfilService:

    @staticmethod
    def list_all() -> list[dict]:
        """
        Daftar semua profil pengurus aktif, diurutkan berdasarkan field `urutan`.
        Dipakai oleh endpoint publik.
        """
        docs = list(
            db.collection(COLLECTION)
            .order_by("urutan")
            .stream()
        )
        return [_doc_to_dict(d) for d in docs]

    @staticmethod
    def get_by_id(profil_id: str) -> dict | None:
        doc = db.collection(COLLECTION).document(profil_id).get()
        return _doc_to_dict(doc) if doc.exists else None

    @staticmethod
    def create(data: dict) -> dict:
        """Tambah anggota kepengurusan baru."""
        now = datetime.now(timezone.utc)
        payload = {
            **data,
            "created_at": now,
            "updated_at": now,
        }
        ref = db.collection(COLLECTION).document()
        ref.set(payload)
        return _doc_to_dict(ref.get())

    @staticmethod
    def update(profil_id: str, data: dict) -> dict | None:
        """Update data profil. Returns None jika tidak ditemukan."""
        ref = db.collection(COLLECTION).document(profil_id)
        if not ref.get().exists:
            return None

        data["updated_at"] = datetime.now(timezone.utc)
        ref.update(data)
        return _doc_to_dict(ref.get())

    @staticmethod
    def delete(profil_id: str) -> bool:
        ref = db.collection(COLLECTION).document(profil_id)
        if not ref.get().exists:
            return False
        ref.delete()
        return True
