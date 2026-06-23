"""
proker/views.py
View untuk modul Program Kerja.
"""

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from core.authentication import FirebaseAuthentication
from core.permissions import IsAdminUser
from core.responses import success_response, error_response, paginated_response

from .services import ProkerService
from .serializers import ProkerSerializer, ProkerCreateSerializer, ProkerUpdateSerializer


class ProkerListView(APIView):
    """GET /api/proker/ — Daftar proker (publik, filter bulan/tahun/bidang/status)."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        page = int(request.query_params.get("page", 1))
        limit = int(request.query_params.get("limit", 20))
        bulan_str = request.query_params.get("bulan")
        tahun_str = request.query_params.get("tahun")
        bidang = request.query_params.get("bidang")
        status = request.query_params.get("status")

        bulan = int(bulan_str) if bulan_str and bulan_str.isdigit() else None
        tahun = int(tahun_str) if tahun_str and tahun_str.isdigit() else None

        result = ProkerService.list_public(
            page=page, limit=limit, bulan=bulan, tahun=tahun, bidang=bidang, status=status
        )
        serialized = ProkerSerializer(result["results"], many=True).data
        return paginated_response(serialized, result["meta"])


class AdminProkerListCreateView(APIView):
    """
    GET  /api/admin/proker/
    POST /api/admin/proker/
    """

    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsAdminUser]

    def get(self, request):
        page = int(request.query_params.get("page", 1))
        limit = int(request.query_params.get("limit", 20))
        bidang = request.query_params.get("bidang")

        result = ProkerService.list_admin(page=page, limit=limit, bidang=bidang)
        serialized = ProkerSerializer(result["results"], many=True).data
        return paginated_response(serialized, result["meta"])

    def post(self, request):
        serializer = ProkerCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response("Data tidak valid.", errors=serializer.errors, status_code=422)

        proker = ProkerService.create(serializer.validated_data)
        return success_response(
            ProkerSerializer(proker).data,
            message="Program kerja berhasil ditambahkan.",
            status_code=201,
        )


class AdminProkerDetailView(APIView):
    """
    GET    /api/admin/proker/<proker_id>/
    PUT    /api/admin/proker/<proker_id>/
    DELETE /api/admin/proker/<proker_id>/
    """

    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsAdminUser]

    def get(self, request, proker_id: str):
        proker = ProkerService.get_by_id(proker_id)
        if not proker:
            return error_response("Program kerja tidak ditemukan.", status_code=404)
        return success_response(ProkerSerializer(proker).data)

    def put(self, request, proker_id: str):
        serializer = ProkerUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response("Data tidak valid.", errors=serializer.errors, status_code=422)

        proker = ProkerService.update(proker_id, serializer.validated_data)
        if proker is None:
            return error_response("Program kerja tidak ditemukan.", status_code=404)
        return success_response(
            ProkerSerializer(proker).data,
            message="Program kerja berhasil diperbarui.",
        )

    def delete(self, request, proker_id: str):
        deleted = ProkerService.delete(proker_id)
        if not deleted:
            return error_response("Program kerja tidak ditemukan.", status_code=404)
        return success_response(None, message="Program kerja berhasil dihapus.")
