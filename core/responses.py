"""
core/responses.py
Helper untuk membentuk response JSON yang konsisten di seluruh API.

Format standar (sesuai BAB 4.5):
{
    "status":  "success" | "error",
    "message": "Pesan deskriptif",
    "data":    { ... } | [ ... ] | null,
    "errors":  { field: [msg] } | null
}

Cara pakai:
    from core.responses import success_response, error_response

    return success_response(data=serializer.data, message="Berhasil")
    return error_response(message="Tidak ditemukan", status_code=404)
"""

from rest_framework.response import Response


def success_response(
    data=None,
    message: str = "Berhasil",
    status_code: int = 200,
) -> Response:
    """Response sukses dengan HTTP 2xx."""
    return Response(
        {
            "status": "success",
            "message": message,
            "data": data,
            "errors": None,
        },
        status=status_code,
    )


def error_response(
    message: str = "Terjadi kesalahan",
    errors=None,
    status_code: int = 400,
) -> Response:
    """Response error dengan HTTP 4xx/5xx."""
    return Response(
        {
            "status": "error",
            "message": message,
            "data": None,
            "errors": errors,
        },
        status=status_code,
    )


def paginated_response(
    results,
    meta: dict,
    message: str = "Berhasil",
    status_code: int = 200,
) -> Response:
    """Response untuk data terpaginasi."""
    return Response(
        {
            "status": "success",
            "message": message,
            "data": {
                "results": results,
                "meta": meta,
            },
            "errors": None,
        },
        status=status_code,
    )
