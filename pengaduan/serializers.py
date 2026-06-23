"""
pengaduan/serializers.py
DRF Serializers untuk modul Pengaduan & Pengajuan Surat.
"""

from rest_framework import serializers

STATUS_CHOICES = ["diterima", "diproses", "selesai"]


class PengaduanSubmitSerializer(serializers.Serializer):
    """Input serializer — form publik pengaduan/pengajuan surat."""

    email = serializers.EmailField(
        help_text="Alamat email pengirim untuk menerima konfirmasi."
    )
    asal_pimpinan = serializers.CharField(
        max_length=255,
        help_text='Nama organisasi pengirim, mis. "PD IPM Kab. Bandung".',
    )
    perihal = serializers.CharField(
        max_length=255,
        help_text="Perihal pengaduan atau surat yang diajukan.",
    )
    isi = serializers.CharField(
        help_text="Isi lengkap pengaduan atau pengajuan surat."
    )
    # `lampiran` (file) diproses di view, tidak di sini


class PengaduanSerializer(serializers.Serializer):
    """Output serializer — response admin (daftar & detail)."""

    id = serializers.CharField(read_only=True)
    email = serializers.EmailField()
    asal_pimpinan = serializers.CharField()
    perihal = serializers.CharField()
    isi = serializers.CharField()
    lampiran_url = serializers.CharField(allow_null=True, default=None)
    status = serializers.CharField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()


class PengaduanPublicResponseSerializer(serializers.Serializer):
    """Output ringkas untuk respons setelah submit (tidak expose semua data)."""

    id = serializers.CharField(read_only=True)
    status = serializers.CharField()
    created_at = serializers.DateTimeField()


class UpdateStatusSerializer(serializers.Serializer):
    """Input untuk PATCH /api/admin/pengaduan/<id>/status/"""

    status = serializers.ChoiceField(choices=STATUS_CHOICES)
