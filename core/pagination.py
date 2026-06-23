"""
core/pagination.py
Helper pagination untuk query Firestore.
Firestore tidak punya built-in "COUNT(*)", jadi kita hitung manual dari stream.

Catatan performa: untuk koleksi sangat besar (>10.000 dokumen), pertimbangkan
menyimpan counter di dokumen terpisah dan paginasi berbasis cursor (start_after).
Untuk skala PW IPM Jabar saat ini, pendekatan ini sudah cukup.
"""

DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 50


def paginate_list(docs: list, page: int, limit: int) -> tuple[list, dict]:
    """
    Paginasi manual dari list dokumen Firestore yang sudah di-stream.

    Args:
        docs:  List dokumen (sudah di-stream dari Firestore)
        page:  Nomor halaman (mulai dari 1)
        limit: Jumlah item per halaman

    Returns:
        (paged_docs, meta_dict)
    """
    limit = min(max(1, limit), MAX_PAGE_SIZE)
    page = max(1, page)
    total = len(docs)
    total_pages = (total + limit - 1) // limit if total > 0 else 1
    offset = (page - 1) * limit
    paged = docs[offset : offset + limit]

    meta = {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages,
    }
    return paged, meta
