"""
profil/serializers.py
DRF Serializers untuk modul Profil Kepengurusan.
"""

from rest_framework import serializers


class ProfilSerializer(serializers.Serializer):
    """Output serializer."""

    id = serializers.CharField(read_only=True)
    nama = serializers.CharField()
    jabatan = serializers.CharField()
    bidang = serializers.CharField()
    foto_url = serializers.CharField(allow_null=True, allow_blank=True, default=None)
    periode_mulai = serializers.DateTimeField(allow_null=True)
    periode_selesai = serializers.DateTimeField(allow_null=True)
    urutan = serializers.IntegerField(default=99)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class ProfilCreateSerializer(serializers.Serializer):
    """Input serializer untuk POST /api/admin/profil/"""

    nama = serializers.CharField(max_length=255)
    jabatan = serializers.CharField(max_length=255)
    bidang = serializers.CharField(max_length=255)
    foto_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    periode_mulai = serializers.DateTimeField(required=False, allow_null=True)
    periode_selesai = serializers.DateTimeField(required=False, allow_null=True)
    urutan = serializers.IntegerField(required=False, default=99, min_value=1)


class ProfilUpdateSerializer(serializers.Serializer):
    """Input serializer untuk PUT /api/admin/profil/<id>/"""

    nama = serializers.CharField(max_length=255, required=False)
    jabatan = serializers.CharField(max_length=255, required=False)
    bidang = serializers.CharField(max_length=255, required=False)
    foto_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    periode_mulai = serializers.DateTimeField(required=False, allow_null=True)
    periode_selesai = serializers.DateTimeField(required=False, allow_null=True)
    urutan = serializers.IntegerField(required=False, min_value=1)

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError("Tidak ada field yang diperbarui.")
        return attrs
