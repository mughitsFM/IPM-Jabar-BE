"""
accounts/views.py
View untuk modul Autentikasi & Manajemen Admin.

Endpoint:
- POST /api/auth/session       → verifikasi ID Token & kembalikan profil (auth_urls.py)
- GET  /api/admin/dashboard/summary/ → ringkasan angka untuk dashboard (dashboard_urls.py)
- GET/POST /api/admin/pengguna/         → daftar & buat akun admin (admin_urls.py)
- PATCH   /api/admin/pengguna/<uid>/   → update role/status admin (admin_urls.py)
"""

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from core.authentication import FirebaseAuthentication
from core.permissions import IsAdminUser, IsSuperAdmin
from core.responses import success_response, error_response, paginated_response

from .services import AccountsService
from .serializers import (
    SessionSerializer,
    AdminProfileSerializer,
    CreateAdminSerializer,
    UpdateAdminSerializer,
    DashboardSummarySerializer,
)


# ── Auth ──────────────────────────────────────────────────────────────────────

class SessionView(APIView):
    """
    POST /api/auth/session
    Menerima ID Token (sudah diverifikasi FirebaseAuthentication),
    lalu mengembalikan profil admin dari Firestore.

    Kenapa endpoint ini ada?
    FE perlu tahu: nama, role, dan status_aktif — info yang ada di Firestore admin_profiles,
    bukan di decoded token. Endpoint ini adalah "handshake" setelah login Firebase.
    """

    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsAdminUser]

    def post(self, request):
        profile = AccountsService.get_session_profile(request.user.uid)
        if not profile:
            return error_response(
                "Profil admin tidak ditemukan. Hubungi Super Admin.",
                status_code=403,
            )

        if not profile.get("status_aktif", True):
            return error_response(
                "Akun Anda telah dinonaktifkan. Hubungi Super Admin.",
                status_code=403,
            )

        return success_response(
            SessionSerializer(profile).data,
            message="Login berhasil.",
        )


# ── Dashboard ─────────────────────────────────────────────────────────────────

class DashboardSummaryView(APIView):
    """GET /api/admin/dashboard/summary/ — Ringkasan angka untuk dashboard admin."""

    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsAdminUser]

    def get(self, request):
        summary = AccountsService.get_dashboard_summary()
        return success_response(
            DashboardSummarySerializer(summary).data,
            message="Data dashboard berhasil diambil.",
        )


# ── Manajemen Pengguna Admin (Super Admin only) ───────────────────────────────

class AdminPenggunaListCreateView(APIView):
    """
    GET  /api/admin/pengguna/ → daftar akun admin
    POST /api/admin/pengguna/ → buat akun admin baru
    (khusus super_admin)
    """

    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        page = int(request.query_params.get("page", 1))
        limit = int(request.query_params.get("limit", 20))
        result = AccountsService.list_admins(page=page, limit=limit)
        serialized = AdminProfileSerializer(result["results"], many=True).data
        return paginated_response(serialized, result["meta"])

    def post(self, request):
        serializer = CreateAdminSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                "Data tidak valid.", errors=serializer.errors, status_code=422
            )

        d = serializer.validated_data
        try:
            profile = AccountsService.create_admin(
                email=d["email"],
                password=d["password"],
                nama=d["nama"],
                role=d["role"],
            )
        except ValueError as e:
            return error_response(str(e), status_code=400)

        return success_response(
            AdminProfileSerializer(profile).data,
            message="Akun admin berhasil dibuat.",
            status_code=201,
        )


class AdminPenggunaUpdateView(APIView):
    """
    PATCH /api/admin/pengguna/<uid>/ → update nama/role/status_aktif
    (khusus super_admin)
    """

    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsSuperAdmin]

    def patch(self, request, uid: str):
        # Cegah super admin menonaktifkan/mengubah akun sendiri
        if uid == request.user.uid:
            return error_response(
                "Tidak dapat mengubah akun Anda sendiri melalui endpoint ini.",
                status_code=400,
            )

        serializer = UpdateAdminSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                "Data tidak valid.", errors=serializer.errors, status_code=422
            )

        try:
            profile = AccountsService.update_admin(uid, serializer.validated_data)
        except ValueError as e:
            return error_response(str(e), status_code=400)

        if profile is None:
            return error_response("Akun admin tidak ditemukan.", status_code=404)

        return success_response(
            AdminProfileSerializer(profile).data,
            message="Akun admin berhasil diperbarui.",
        )
