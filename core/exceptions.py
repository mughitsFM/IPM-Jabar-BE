"""
core/exceptions.py
Custom exception handler DRF.
Dipasang di REST_FRAMEWORK["EXCEPTION_HANDLER"] pada settings.py.

Tujuan:
1. Memastikan semua error response mengikuti format standar (status/message/errors)
2. Mencegah stack trace bocor ke klien di production
3. Menangani exception tak terduga dengan HTTP 500 yang informatif
"""

import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context) -> Response:
    """
    Dipanggil DRF setiap kali ada exception yang tidak di-handle view.
    Mengembalikan format response standar {status, message, data, errors}.
    """
    # Biarkan DRF menangani dulu (AuthenticationFailed, NotAuthenticated, dll.)
    response = exception_handler(exc, context)

    if response is not None:
        # DRF sudah menangani → reformat saja
        original_data = response.data

        # DRF kadang taruh error sebagai list di bawah "detail" atau "non_field_errors"
        if isinstance(original_data, dict):
            message = original_data.get("detail", "Terjadi kesalahan")
            if hasattr(message, "default_code"):
                message = str(message)
            errors = {k: v for k, v in original_data.items() if k != "detail"}
            errors = errors or None
        else:
            message = str(original_data)
            errors = None

        response.data = {
            "status": "error",
            "message": message,
            "data": None,
            "errors": errors,
        }
        return response

    # Exception tidak dikenal DRF (mis. bug, RuntimeError, dsb.) → HTTP 500
    logger.exception(
        "Unhandled exception di %s", context.get("view", "unknown view"), exc_info=exc
    )
    return Response(
        {
            "status": "error",
            "message": "Kesalahan internal server. Silakan coba lagi nanti.",
            "data": None,
            "errors": None,
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
