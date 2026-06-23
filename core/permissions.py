"""
core/permissions.py
Custom DRF Permission classes berbasis role dari Firebase custom claims.

Role yang ada:
- "super_admin" : akses penuh (semua endpoint admin + pengguna)
- "editor"      : akses terbatas (kelola berita & proker, baca pengaduan)

Cara pakai di view:
    from core.permissions import IsAdminUser, IsSuperAdmin
    permission_classes = [IsAdminUser]
"""

from rest_framework.permissions import BasePermission

ROLE_SUPER_ADMIN = "super_admin"
ROLE_EDITOR = "editor"
ALL_ADMIN_ROLES = {ROLE_SUPER_ADMIN, ROLE_EDITOR}


class IsAdminUser(BasePermission):
    """
    Mengizinkan akses untuk user dengan role 'editor' atau 'super_admin'.
    Dipakai di semua endpoint admin umum (CRUD berita, profil, proker, pengaduan).
    """

    message = "Akses ditolak. Diperlukan akun admin yang valid."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "role", None) in ALL_ADMIN_ROLES
        )


class IsSuperAdmin(BasePermission):
    """
    Mengizinkan akses hanya untuk 'super_admin'.
    Dipakai untuk manajemen akun admin (tambah, ubah role, nonaktifkan).
    """

    message = "Akses ditolak. Hanya Super Admin yang dapat mengakses fitur ini."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "role", None) == ROLE_SUPER_ADMIN
        )
