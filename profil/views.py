"""
profil/views.py
View tipis untuk modul Profil Kepengurusan.
"""

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from core.authentication import FirebaseAuthentication
from core.permissions import IsAdminUser
from core.responses import success_response, error_response

from .services import ProfilService
from .serializers import ProfilSerializer, ProfilCreateSerializer, ProfilUpdateSerializer
from storage_files.services import FileUploadService


class ProfilListView(APIView):
    """GET /api/profil/ — Daftar profil kepengurusan (publik)."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        profil_list = ProfilService.list_all()
        return success_response(ProfilSerializer(profil_list, many=True).data)


class AdminProfilListCreateView(APIView):
    """
    GET  /api/admin/profil/ — Daftar profil (admin)
    POST /api/admin/profil/ — Tambah profil baru
    """

    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        profil_list = ProfilService.list_all()
        return success_response(ProfilSerializer(profil_list, many=True).data)

    def post(self, request):
        serializer = ProfilCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response("Data tidak valid.", errors=serializer.errors, status_code=422)

        data = serializer.validated_data

        # Upload foto jika ada
        foto_file = request.FILES.get("foto")
        if foto_file:
            try:
                data["foto_url"] = FileUploadService.upload_image(foto_file, folder="profil")
            except ValueError as e:
                return error_response(str(e), status_code=400)

        profil = ProfilService.create(data)
        return success_response(
            ProfilSerializer(profil).data,
            message="Profil berhasil ditambahkan.",
            status_code=201,
        )


class AdminProfilDetailView(APIView):
    """
    GET    /api/admin/profil/<profil_id>/
    PUT    /api/admin/profil/<profil_id>/
    DELETE /api/admin/profil/<profil_id>/
    """

    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request, profil_id: str):
        profil = ProfilService.get_by_id(profil_id)
        if not profil:
            return error_response("Profil tidak ditemukan.", status_code=404)
        return success_response(ProfilSerializer(profil).data)

    def put(self, request, profil_id: str):
        serializer = ProfilUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response("Data tidak valid.", errors=serializer.errors, status_code=422)

        data = serializer.validated_data

        foto_file = request.FILES.get("foto")
        if foto_file:
            try:
                data["foto_url"] = FileUploadService.upload_image(foto_file, folder="profil")
            except ValueError as e:
                return error_response(str(e), status_code=400)

        profil = ProfilService.update(profil_id, data)
        if profil is None:
            return error_response("Profil tidak ditemukan.", status_code=404)
        return success_response(ProfilSerializer(profil).data, message="Profil berhasil diperbarui.")

    def delete(self, request, profil_id: str):
        deleted = ProfilService.delete(profil_id)
        if not deleted:
            return error_response("Profil tidak ditemukan.", status_code=404)
        return success_response(None, message="Profil berhasil dihapus.")
