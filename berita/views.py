"""
berita/views.py
View untuk modul Berita — tipis, hanya handle HTTP.
Logika bisnis ada di berita/services.py.
"""

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from core.authentication import FirebaseAuthentication
from core.permissions import IsAdminUser
from core.responses import success_response, error_response, paginated_response

from .services import BeritaService
from .serializers import (
    BeritaSerializer,
    BeritaListItemSerializer,
    BeritaCreateSerializer,
    BeritaUpdateSerializer,
)
from storage_files.services import FileUploadService


# ── Public Views ───────────────────────────────────────────────────────────────

class BeritaListView(APIView):
    """GET /api/berita/ — Daftar berita terpublikasi (publik)."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        page = int(request.query_params.get("page", 1))
        limit = int(request.query_params.get("limit", 10))
        kategori = request.query_params.get("kategori")

        result = BeritaService.list_published(page=page, limit=limit, kategori=kategori)
        serialized = BeritaListItemSerializer(result["results"], many=True).data
        return paginated_response(serialized, result["meta"])


class BeritaDetailView(APIView):
    """GET /api/berita/<slug>/ — Detail berita (publik)."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request, slug: str):
        berita = BeritaService.get_by_slug(slug)
        if not berita:
            return error_response("Berita tidak ditemukan.", status_code=404)

        return success_response(BeritaSerializer(berita).data)


# ── Admin Views ────────────────────────────────────────────────────────────────

class AdminBeritaListCreateView(APIView):
    """
    GET  /api/admin/berita/ — Semua berita (semua status) dengan filter
    POST /api/admin/berita/ — Buat berita baru (support upload thumbnail)
    """

    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        page = int(request.query_params.get("page", 1))
        limit = int(request.query_params.get("limit", 10))
        status_filter = request.query_params.get("status")
        kategori = request.query_params.get("kategori")

        result = BeritaService.list_all_admin(
            page=page, limit=limit, status=status_filter, kategori=kategori
        )
        serialized = BeritaSerializer(result["results"], many=True).data
        return paginated_response(serialized, result["meta"])

    def post(self, request):
        serializer = BeritaCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                "Data tidak valid.", errors=serializer.errors, status_code=422
            )

        data = serializer.validated_data

        # Upload thumbnail jika ada
        thumbnail_file = request.FILES.get("thumbnail")
        if thumbnail_file:
            try:
                data["thumbnail_url"] = FileUploadService.upload_image(
                    thumbnail_file, folder="berita"
                )
            except ValueError as e:
                return error_response(str(e), status_code=400)

        try:
            berita = BeritaService.create(data, user_uid=request.user.uid)
        except ValueError as e:
            return error_response(str(e), status_code=400)

        return success_response(
            BeritaSerializer(berita).data,
            message="Berita berhasil dibuat.",
            status_code=201,
        )


class AdminBeritaDetailView(APIView):
    """
    GET    /api/admin/berita/<berita_id>/ — Detail berita (admin)
    PUT    /api/admin/berita/<berita_id>/ — Update berita
    DELETE /api/admin/berita/<berita_id>/ — Hapus berita
    """

    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request, berita_id: str):
        berita = BeritaService.get_by_id(berita_id)
        if not berita:
            return error_response("Berita tidak ditemukan.", status_code=404)
        return success_response(BeritaSerializer(berita).data)

    def put(self, request, berita_id: str):
        serializer = BeritaUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                "Data tidak valid.", errors=serializer.errors, status_code=422
            )

        data = serializer.validated_data

        # Upload thumbnail baru jika ada
        thumbnail_file = request.FILES.get("thumbnail")
        if thumbnail_file:
            try:
                data["thumbnail_url"] = FileUploadService.upload_image(
                    thumbnail_file, folder="berita"
                )
            except ValueError as e:
                return error_response(str(e), status_code=400)

        try:
            berita = BeritaService.update(berita_id, data)
        except ValueError as e:
            return error_response(str(e), status_code=400)

        if berita is None:
            return error_response("Berita tidak ditemukan.", status_code=404)

        return success_response(BeritaSerializer(berita).data, message="Berita berhasil diperbarui.")

    def delete(self, request, berita_id: str):
        deleted = BeritaService.delete(berita_id)
        if not deleted:
            return error_response("Berita tidak ditemukan.", status_code=404)
        return success_response(None, message="Berita berhasil dihapus.")
