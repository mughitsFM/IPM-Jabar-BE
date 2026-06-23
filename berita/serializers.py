"""
berita/serializers.py
DRF Serializers untuk modul Berita.

Catatan: Memakai plain Serializer (bukan ModelSerializer) karena data ada di Firestore,
bukan di Django ORM. Validasi tetap dilakukan di sini.
"""

from rest_framework import serializers

KATEGORI_CHOICES = ["kegiatan", "umum", "surat_resmi"]
STATUS_CHOICES = ["draft", "terjadwal", "dipublikasikan"]


class BeritaSerializer(serializers.Serializer):
    """Output serializer — untuk response GET (list & detail)."""

    id = serializers.CharField(read_only=True)
    judul = serializers.CharField()
    slug = serializers.CharField()
    konten = serializers.CharField()
    kategori = serializers.CharField()
    thumbnail_url = serializers.CharField(allow_null=True, allow_blank=True, default=None)
    status = serializers.CharField()
    published_at = serializers.DateTimeField(allow_null=True, default=None)
    user_id = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class BeritaListItemSerializer(serializers.Serializer):
    """Serializer ringkas untuk tampilan kartu di daftar berita (tanpa field konten penuh)."""

    id = serializers.CharField(read_only=True)
    judul = serializers.CharField()
    slug = serializers.CharField()
    kategori = serializers.CharField()
    thumbnail_url = serializers.CharField(allow_null=True, allow_blank=True, default=None)
    status = serializers.CharField()
    published_at = serializers.DateTimeField(allow_null=True, default=None)
    created_at = serializers.DateTimeField(read_only=True)


class BeritaCreateSerializer(serializers.Serializer):
    """Input serializer untuk POST /api/admin/berita/"""

    judul = serializers.CharField(max_length=255)
    slug = serializers.SlugField(
        max_length=255,
        help_text="URL-friendly identifier, hanya huruf kecil, angka, dan tanda hubung.",
    )
    konten = serializers.CharField(
        help_text="Konten artikel dalam format HTML (dari rich-text editor)."
    )
    kategori = serializers.ChoiceField(choices=KATEGORI_CHOICES)
    thumbnail_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    status = serializers.ChoiceField(choices=STATUS_CHOICES, default="draft")
    published_at = serializers.DateTimeField(required=False, allow_null=True)


class BeritaUpdateSerializer(serializers.Serializer):
    """Input serializer untuk PUT /api/admin/berita/<id>/"""

    judul = serializers.CharField(max_length=255, required=False)
    slug = serializers.SlugField(max_length=255, required=False)
    konten = serializers.CharField(required=False)
    kategori = serializers.ChoiceField(choices=KATEGORI_CHOICES, required=False)
    thumbnail_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    status = serializers.ChoiceField(choices=STATUS_CHOICES, required=False)
    published_at = serializers.DateTimeField(required=False, allow_null=True)

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError("Tidak ada field yang diperbarui.")
        return attrs
