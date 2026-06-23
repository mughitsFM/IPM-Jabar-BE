"""
proker/serializers.py
DRF Serializers untuk modul Program Kerja / Proker.
"""

from rest_framework import serializers

STATUS_CHOICES = ["akan_datang", "berlangsung", "selesai"]
BIDANG_CHOICES = [
    "organisasi", "kader", "kajian_dakwah_islami", "perkaderan",
    "hikmah", "immawan", "immawati", "media_komunikasi", "lainnya",
]


class ProkerSerializer(serializers.Serializer):
    """Output serializer."""

    id = serializers.CharField(read_only=True)
    nama_kegiatan = serializers.CharField()
    deskripsi = serializers.CharField(allow_blank=True, default="")
    tanggal_mulai = serializers.DateTimeField()
    tanggal_selesai = serializers.DateTimeField()
    bidang = serializers.CharField()
    status = serializers.CharField()  # dihitung dinamis di service
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class ProkerCreateSerializer(serializers.Serializer):
    """Input untuk POST /api/admin/proker/"""

    nama_kegiatan = serializers.CharField(max_length=255)
    deskripsi = serializers.CharField(required=False, allow_blank=True, default="")
    tanggal_mulai = serializers.DateTimeField()
    tanggal_selesai = serializers.DateTimeField()
    bidang = serializers.ChoiceField(choices=BIDANG_CHOICES)

    def validate(self, attrs):
        if attrs["tanggal_selesai"] < attrs["tanggal_mulai"]:
            raise serializers.ValidationError(
                "Tanggal selesai tidak boleh sebelum tanggal mulai."
            )
        return attrs


class ProkerUpdateSerializer(serializers.Serializer):
    """Input untuk PUT /api/admin/proker/<id>/"""

    nama_kegiatan = serializers.CharField(max_length=255, required=False)
    deskripsi = serializers.CharField(required=False, allow_blank=True)
    tanggal_mulai = serializers.DateTimeField(required=False)
    tanggal_selesai = serializers.DateTimeField(required=False)
    bidang = serializers.ChoiceField(choices=BIDANG_CHOICES, required=False)

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError("Tidak ada field yang diperbarui.")
        mulai = attrs.get("tanggal_mulai")
        selesai = attrs.get("tanggal_selesai")
        if mulai and selesai and selesai < mulai:
            raise serializers.ValidationError(
                "Tanggal selesai tidak boleh sebelum tanggal mulai."
            )
        return attrs
