"""
proker/services.py
Service layer untuk modul Timeline / Kalender Program Kerja.
Firestore collection: "program_kerja"
"""

from datetime import datetime, timezone
from core.firebase_client import db
from core.pagination import paginate_list, DEFAULT_PAGE_SIZE

COLLECTION = "program_kerja"
STATUS_AKAN_DATANG = "akan_datang"
STATUS_BERLANGSUNG = "berlangsung"
STATUS_SELESAI = "selesai"


def _doc_to_dict(doc) -> dict:
    d = doc.to_dict() or {}
    d["id"] = doc.id
    return d


def _compute_status(tanggal_mulai, tanggal_selesai) -> str:
    """
    Hitung status proker secara dinamis berdasarkan tanggal saat ini.
    Dipanggil saat membaca data agar selalu up-to-date.
    """
    now = datetime.now(timezone.utc)
    try:
        # Firestore mengembalikan datetime dengan timezone, pastikan konsisten
        mulai = tanggal_mulai.replace(tzinfo=timezone.utc) if tanggal_mulai.tzinfo is None else tanggal_mulai
        selesai = tanggal_selesai.replace(tzinfo=timezone.utc) if tanggal_selesai.tzinfo is None else tanggal_selesai

        if now < mulai:
            return STATUS_AKAN_DATANG
        elif mulai <= now <= selesai:
            return STATUS_BERLANGSUNG
        else:
            return STATUS_SELESAI
    except Exception:
        return STATUS_AKAN_DATANG


class ProkerService:

    @staticmethod
    def list_public(
        page: int = 1,
        limit: int = DEFAULT_PAGE_SIZE,
        bulan: int = None,
        tahun: int = None,
        bidang: str = None,
        status: str = None,
    ) -> dict:
        """Daftar proker untuk halaman publik (kalender/timeline)."""
        query = db.collection(COLLECTION).order_by("tanggal_mulai")

        if bidang:
            query = query.where("bidang", "==", bidang)

        all_docs = list(query.stream())
        results = [_doc_to_dict(d) for d in all_docs]

        # Filter bulan/tahun secara in-memory (Firestore tidak support range filter dua field sekaligus tanpa composite index khusus)
        if bulan or tahun:
            filtered = []
            for item in results:
                tm = item.get("tanggal_mulai")
                if tm:
                    dt = tm if hasattr(tm, "month") else None
                    if dt:
                        if bulan and dt.month != bulan:
                            continue
                        if tahun and dt.year != tahun:
                            continue
                filtered.append(item)
            results = filtered

        # Hitung status dinamis
        for item in results:
            tm = item.get("tanggal_mulai")
            ts = item.get("tanggal_selesai")
            if tm and ts:
                item["status"] = _compute_status(tm, ts)

        # Filter status setelah kalkulasi
        if status:
            results = [r for r in results if r.get("status") == status]

        # Pagination manual
        total = len(results)
        from core.pagination import DEFAULT_PAGE_SIZE
        offset = (page - 1) * limit
        paged = results[offset: offset + limit]
        meta = {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit if total > 0 else 1,
        }

        return {"results": paged, "meta": meta}

    @staticmethod
    def list_admin(
        page: int = 1,
        limit: int = DEFAULT_PAGE_SIZE,
        bidang: str = None,
    ) -> dict:
        """Daftar proker untuk panel admin."""
        return ProkerService.list_public(page=page, limit=limit, bidang=bidang)

    @staticmethod
    def get_by_id(proker_id: str) -> dict | None:
        doc = db.collection(COLLECTION).document(proker_id).get()
        return _doc_to_dict(doc) if doc.exists else None

    @staticmethod
    def create(data: dict) -> dict:
        now = datetime.now(timezone.utc)
        payload = {
            **data,
            "created_at": now,
            "updated_at": now,
        }
        ref = db.collection(COLLECTION).document()
        ref.set(payload)
        result = _doc_to_dict(ref.get())
        if result.get("tanggal_mulai") and result.get("tanggal_selesai"):
            result["status"] = _compute_status(result["tanggal_mulai"], result["tanggal_selesai"])
        return result

    @staticmethod
    def update(proker_id: str, data: dict) -> dict | None:
        ref = db.collection(COLLECTION).document(proker_id)
        if not ref.get().exists:
            return None
        data["updated_at"] = datetime.now(timezone.utc)
        ref.update(data)
        result = _doc_to_dict(ref.get())
        if result.get("tanggal_mulai") and result.get("tanggal_selesai"):
            result["status"] = _compute_status(result["tanggal_mulai"], result["tanggal_selesai"])
        return result

    @staticmethod
    def delete(proker_id: str) -> bool:
        ref = db.collection(COLLECTION).document(proker_id)
        if not ref.get().exists:
            return False
        ref.delete()
        return True

    @staticmethod
    def count_active() -> int:
        """Hitung proker yang sedang berlangsung (untuk dashboard)."""
        docs = list(db.collection(COLLECTION).stream())
        count = 0
        for doc in docs:
            d = doc.to_dict() or {}
            tm = d.get("tanggal_mulai")
            ts = d.get("tanggal_selesai")
            if tm and ts and _compute_status(tm, ts) == STATUS_BERLANGSUNG:
                count += 1
        return count
