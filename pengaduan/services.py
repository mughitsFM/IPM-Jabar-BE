"""
pengaduan/services.py
Service layer untuk modul Pengaduan & Pengajuan Surat.
Firestore collection: "pengaduan"
"""

from datetime import datetime, timezone
from core.firebase_client import db
from core.pagination import paginate_list, DEFAULT_PAGE_SIZE
from .emails import kirim_konfirmasi_pengirim, kirim_notifikasi_admin

COLLECTION = "pengaduan"
STATUS_DITERIMA = "diterima"
STATUS_DIPROSES = "diproses"
STATUS_SELESAI = "selesai"
VALID_STATUS = {STATUS_DITERIMA, STATUS_DIPROSES, STATUS_SELESAI}


def _doc_to_dict(doc) -> dict:
    d = doc.to_dict() or {}
    d["id"] = doc.id
    return d


class PengaduanService:

    @staticmethod
    def create(data: dict, lampiran_url: str = None) -> dict:
        """
        Simpan pengaduan baru ke Firestore.
        Setelah simpan, kirim email konfirmasi ke pengirim & notifikasi ke admin.

        Args:
            data:         Validated data dari serializer
            lampiran_url: URL Firebase Storage jika ada lampiran
        """
        now = datetime.now(timezone.utc)
        payload = {
            **data,
            "lampiran_url": lampiran_url,
            "status": STATUS_DITERIMA,
            "created_at": now,
            "updated_at": now,
        }

        ref = db.collection(COLLECTION).document()
        ref.set(payload)
        result = _doc_to_dict(ref.get())

        # Kirim email (fire-and-forget, error tidak memblok response)
        kirim_konfirmasi_pengirim(
            email=data["email"],
            perihal=data["perihal"],
            asal_pimpinan=data["asal_pimpinan"],
        )
        kirim_notifikasi_admin(data)

        return result

    @staticmethod
    def list_admin(
        page: int = 1,
        limit: int = DEFAULT_PAGE_SIZE,
        status: str = None,
    ) -> dict:
        """Daftar semua pengaduan untuk panel admin, terbaru di atas."""
        query = db.collection(COLLECTION).order_by("created_at", direction="DESCENDING")
        if status:
            query = query.where("status", "==", status)

        all_docs = list(query.stream())
        paged_docs, meta = paginate_list(all_docs, page, limit)

        return {
            "results": [_doc_to_dict(d) for d in paged_docs],
            "meta": meta,
        }

    @staticmethod
    def get_by_id(pengaduan_id: str) -> dict | None:
        doc = db.collection(COLLECTION).document(pengaduan_id).get()
        return _doc_to_dict(doc) if doc.exists else None

    @staticmethod
    def update_status(pengaduan_id: str, status: str) -> dict | None:
        """
        Ubah status pengaduan.
        Raises: ValueError jika status tidak valid
        Returns: None jika dokumen tidak ditemukan
        """
        if status not in VALID_STATUS:
            raise ValueError(
                f"Status tidak valid. Pilihan: {', '.join(sorted(VALID_STATUS))}"
            )

        ref = db.collection(COLLECTION).document(pengaduan_id)
        if not ref.get().exists:
            return None

        ref.update({
            "status": status,
            "updated_at": datetime.now(timezone.utc),
        })
        return _doc_to_dict(ref.get())

    @staticmethod
    def count_incoming() -> int:
        """Hitung pengaduan berstatus 'diterima' (belum diproses) untuk dashboard."""
        docs = list(
            db.collection(COLLECTION)
            .where("status", "==", STATUS_DITERIMA)
            .stream()
        )
        return len(docs)
