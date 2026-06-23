"""
berita/services.py
Service layer untuk modul Berita & Informasi.

Tanggung jawab:
- Semua query & mutasi ke Firestore collection "berita"
- Validasi slug unik
- Set timestamp otomatis
- Sanitasi konten HTML (XSS prevention via bleach)

Dipanggil oleh: berita/views.py (HANYA dari sana)
"""

import bleach
from datetime import datetime, timezone
from core.firebase_client import db
from core.pagination import paginate_list, DEFAULT_PAGE_SIZE

COLLECTION = "berita"

# Tag HTML yang diizinkan di konten rich-text
ALLOWED_TAGS = [
    "p", "br", "strong", "em", "u", "s", "blockquote", "pre", "code",
    "h1", "h2", "h3", "h4",
    "ul", "ol", "li",
    "a", "img",
    "table", "thead", "tbody", "tr", "th", "td",
    "figure", "figcaption",
]
ALLOWED_ATTRIBUTES = {
    "a": ["href", "title", "target", "rel"],
    "img": ["src", "alt", "title", "width", "height"],
    "td": ["colspan", "rowspan"],
    "th": ["colspan", "rowspan"],
}


def _sanitize_html(html_content: str) -> str:
    """Sanitasi HTML untuk mencegah XSS. Dipanggil saat create/update."""
    return bleach.clean(
        html_content,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True,
    )


def _doc_to_dict(doc) -> dict:
    """Konversi Firestore DocumentSnapshot → dict + tambahkan 'id'."""
    d = doc.to_dict() or {}
    d["id"] = doc.id
    return d


class BeritaService:

    # ── Public (tidak butuh auth) ──────────────────────────────────────────────

    @staticmethod
    def list_published(
        page: int = 1,
        limit: int = DEFAULT_PAGE_SIZE,
        kategori: str = None,
    ) -> dict:
        """Daftar berita yang sudah dipublikasikan, dengan pagination."""
        query = (
            db.collection(COLLECTION)
            .where("status", "==", "dipublikasikan")
            .order_by("published_at", direction="DESCENDING")
        )
        if kategori:
            query = query.where("kategori", "==", kategori)

        all_docs = list(query.stream())
        paged_docs, meta = paginate_list(all_docs, page, limit)

        return {
            "results": [_doc_to_dict(d) for d in paged_docs],
            "meta": meta,
        }

    @staticmethod
    def get_by_slug(slug: str) -> dict | None:
        """Detail berita berdasarkan slug (hanya yang sudah dipublikasikan)."""
        docs = list(
            db.collection(COLLECTION)
            .where("slug", "==", slug)
            .where("status", "==", "dipublikasikan")
            .limit(1)
            .stream()
        )
        return _doc_to_dict(docs[0]) if docs else None

    # ── Admin ─────────────────────────────────────────────────────────────────

    @staticmethod
    def list_all_admin(
        page: int = 1,
        limit: int = DEFAULT_PAGE_SIZE,
        status: str = None,
        kategori: str = None,
    ) -> dict:
        """Daftar semua berita (semua status) untuk panel admin."""
        query = db.collection(COLLECTION).order_by("created_at", direction="DESCENDING")
        if status:
            query = query.where("status", "==", status)
        if kategori:
            query = query.where("kategori", "==", kategori)

        all_docs = list(query.stream())
        paged_docs, meta = paginate_list(all_docs, page, limit)

        return {
            "results": [_doc_to_dict(d) for d in paged_docs],
            "meta": meta,
        }

    @staticmethod
    def get_by_id(berita_id: str) -> dict | None:
        """Ambil satu berita berdasarkan ID (untuk admin edit)."""
        doc = db.collection(COLLECTION).document(berita_id).get()
        return _doc_to_dict(doc) if doc.exists else None

    @staticmethod
    def slug_exists(slug: str, exclude_id: str = None) -> bool:
        """Cek apakah slug sudah dipakai dokumen lain."""
        docs = list(
            db.collection(COLLECTION)
            .where("slug", "==", slug)
            .limit(2)
            .stream()
        )
        if not docs:
            return False
        if exclude_id:
            return any(d.id != exclude_id for d in docs)
        return True

    @staticmethod
    def create(data: dict, user_uid: str) -> dict:
        """
        Buat berita baru.
        Raises:
            ValueError: jika slug sudah digunakan
        """
        slug = data.get("slug", "")
        if BeritaService.slug_exists(slug):
            raise ValueError("Slug sudah digunakan. Pilih slug yang berbeda.")

        now = datetime.now(timezone.utc)
        payload = {
            **data,
            "konten": _sanitize_html(data.get("konten", "")),
            "user_id": user_uid,
            "created_at": now,
            "updated_at": now,
        }

        # Auto-set published_at saat pertama kali dipublikasikan
        if payload.get("status") == "dipublikasikan" and not payload.get("published_at"):
            payload["published_at"] = now

        ref = db.collection(COLLECTION).document()
        ref.set(payload)
        return _doc_to_dict(ref.get())

    @staticmethod
    def update(berita_id: str, data: dict) -> dict | None:
        """
        Update berita yang sudah ada.
        Returns None jika tidak ditemukan.
        Raises:
            ValueError: jika slug sudah digunakan dokumen lain
        """
        ref = db.collection(COLLECTION).document(berita_id)
        existing = ref.get()
        if not existing.exists:
            return None

        if "slug" in data and BeritaService.slug_exists(data["slug"], exclude_id=berita_id):
            raise ValueError("Slug sudah digunakan. Pilih slug yang berbeda.")

        if "konten" in data:
            data["konten"] = _sanitize_html(data["konten"])

        now = datetime.now(timezone.utc)
        data["updated_at"] = now

        existing_data = existing.to_dict() or {}
        if (
            data.get("status") == "dipublikasikan"
            and not existing_data.get("published_at")
            and not data.get("published_at")
        ):
            data["published_at"] = now

        ref.update(data)
        return _doc_to_dict(ref.get())

    @staticmethod
    def delete(berita_id: str) -> bool:
        """Hapus berita. Returns False jika tidak ditemukan."""
        ref = db.collection(COLLECTION).document(berita_id)
        if not ref.get().exists:
            return False
        ref.delete()
        return True

    @staticmethod
    def count_published() -> int:
        """Hitung total berita terpublikasi (untuk dashboard)."""
        docs = list(
            db.collection(COLLECTION)
            .where("status", "==", "dipublikasikan")
            .stream()
        )
        return len(docs)
