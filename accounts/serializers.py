"""
accounts/serializers.py
DRF Serializers untuk modul Autentikasi & Manajemen Admin.
"""

from rest_framework import serializers

ROLE_CHOICES = ["super_admin", "editor"]


class AdminProfileSerializer(serializers.Serializer):
    """Output serializer profil admin (dipakai di session & daftar pengguna)."""

    uid = serializers.CharField(read_only=True)
    nama = serializers.CharField()
    email = serializers.EmailField()
    role = serializers.CharField()
    status_aktif = serializers.BooleanField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class SessionSerializer(serializers.Serializer):
    """Output ringkas untuk POST /api/auth/session."""

    uid = serializers.CharField()
    nama = serializers.CharField()
    email = serializers.EmailField()
    role = serializers.CharField()
    status_aktif = serializers.BooleanField()


class CreateAdminSerializer(serializers.Serializer):
    """Input untuk POST /api/admin/pengguna/ — buat akun admin baru."""

    email = serializers.EmailField()
    password = serializers.CharField(
        min_length=8,
        write_only=True,
        help_text="Minimal 8 karakter.",
    )
    nama = serializers.CharField(max_length=255)
    role = serializers.ChoiceField(choices=ROLE_CHOICES)


class UpdateAdminSerializer(serializers.Serializer):
    """Input untuk PATCH /api/admin/pengguna/<uid>/ — update profil atau role admin."""

    nama = serializers.CharField(max_length=255, required=False)
    role = serializers.ChoiceField(choices=ROLE_CHOICES, required=False)
    status_aktif = serializers.BooleanField(required=False)

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError("Tidak ada field yang diperbarui.")
        return attrs


class DashboardSummarySerializer(serializers.Serializer):
    """Output untuk GET /api/admin/dashboard/summary/"""

    total_berita_published = serializers.IntegerField()
    total_proker_aktif = serializers.IntegerField()
    total_pengaduan_masuk = serializers.IntegerField()
