"""
pengaduan/views.py
View untuk modul Pengaduan & Pengajuan Surat.
"""

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from core.authentication import FirebaseAuthentication
from core.permissions import IsAdminUser
from core.responses import success_response, error_response, paginated_response

from .services import PengaduanService
from .serializers import (
    PengaduanSubmitSerializer,
    PengaduanSerializer,
    PengaduanPublicResponseSerializer,
    UpdateStatusSerializer,
)
from storage_files.services import FileUploadService


class PengaduanCreateView(APIView):
    """POST /api/pengaduan/ — Kirim pengaduan/pengajuan surat (publik)."""

    authentication_classes = []
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        serializer = PengaduanSubmitSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response("Data tidak valid.", errors=serializer.errors, status_code=422)

        data = serializer.validated_data
        lampiran_url = None

        # Upload lampiran jika ada
        lampiran_file = request.FILES.get("lampiran")
        if lampiran_file:
            try:
                lampiran_url = FileUploadService.upload_attachment(
                    lampiran_file, folder="pengaduan-lampiran"
                )
            except ValueError as e:
                return error_response(str(e), status_code=400)

        pengaduan = PengaduanService.create(data, lampiran_url=lampiran_url)
        return success_response(
            PengaduanPublicResponseSerializer(pengaduan).data,
            message=(
                "Pengaduan Anda telah berhasil dikirim. "
                "Kami akan mengirim konfirmasi ke email Anda."
            ),
            status_code=201,
        )


class AdminPengaduanListView(APIView):
    """GET /api/admin/pengaduan/ — Daftar pengaduan masuk (admin)."""

    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsAdminUser]

    def get(self, request):
        page = int(request.query_params.get("page", 1))
        limit = int(request.query_params.get("limit", 10))
        status_filter = request.query_params.get("status")

        result = PengaduanService.list_admin(page=page, limit=limit, status=status_filter)
        serialized = PengaduanSerializer(result["results"], many=True).data
        return paginated_response(serialized, result["meta"])


class AdminPengaduanDetailView(APIView):
    """GET /api/admin/pengaduan/<pengaduan_id>/ — Detail pengaduan (admin)."""

    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsAdminUser]

    def get(self, request, pengaduan_id: str):
        pengaduan = PengaduanService.get_by_id(pengaduan_id)
        if not pengaduan:
            return error_response("Pengaduan tidak ditemukan.", status_code=404)
        return success_response(PengaduanSerializer(pengaduan).data)


class AdminPengaduanStatusView(APIView):
    """PATCH /api/admin/pengaduan/<pengaduan_id>/status/ — Ubah status pengaduan."""

    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsAdminUser]

    def patch(self, request, pengaduan_id: str):
        serializer = UpdateStatusSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response("Data tidak valid.", errors=serializer.errors, status_code=422)

        try:
            pengaduan = PengaduanService.update_status(
                pengaduan_id, serializer.validated_data["status"]
            )
        except ValueError as e:
            return error_response(str(e), status_code=400)

        if pengaduan is None:
            return error_response("Pengaduan tidak ditemukan.", status_code=404)

        return success_response(
            PengaduanSerializer(pengaduan).data,
            message=f"Status pengaduan diperbarui menjadi '{pengaduan['status']}'.",
        )
