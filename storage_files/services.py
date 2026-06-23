"""
storage_files/services.py
Service untuk upload & hapus file via Cloudinary.

Menggantikan Firebase Storage. Alasan:
- Gratis 25 GB (Firebase Storage gratis 5 GB saja)
- CDN global otomatis (edge caching)
- Transformasi gambar server-side: auto WebP, resize, quality:auto
- URL publik permanen tanpa perlu make_public()

Semua upload WAJIB lewat Django — bukan langsung dari klien ke Cloudinary.
Tujuan: validasi MIME type & ukuran dijamin di satu tempat.

Folder di Cloudinary:
- "berita/"              → thumbnail artikel berita
- "profil/"             → foto profil pengurus
- "pengaduan-lampiran/" → lampiran PDF/DOCX pengaduan
"""

import uuid
import re
import logging

import cloudinary
import cloudinary.uploader
import cloudinary.api
from django.conf import settings

logger = logging.getLogger(__name__)

# ─── Konfigurasi Cloudinary (dibaca dari Django settings / .env) ──────────────
def _configure_cloudinary() -> None:
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=settings.CLOUDINARY_SECURE,
    )

_configure_cloudinary()


# ─── Konstanta validasi ────────────────────────────────────────────────────────

# MIME type yang diizinkan untuk lampiran pengaduan
ALLOWED_MIME_ATTACHMENT = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
    "image/jpeg",
    "image/png",
}

# MIME type yang diizinkan untuk gambar (thumbnail & foto profil)
ALLOWED_MIME_IMAGE = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

# Ekstensi Cloudinary sesuai MIME
MIME_TO_EXT = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
}

MAX_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


class FileUploadService:
    """
    Service untuk upload & hapus file via Cloudinary.
    Interface publik identik dengan versi Firebase Storage lama
    sehingga tidak ada view/service lain yang perlu diubah.
    """

    # ── Gambar (thumbnail berita & foto profil) ──────────────────────────────

    @staticmethod
    def upload_image(file, folder: str = "berita") -> str:
        """
        Upload gambar ke Cloudinary dengan transformasi otomatis:
        - Konversi ke WebP (hemat bandwidth ~30%)
        - quality:auto (Cloudinary pilih kualitas terbaik)
        - Disimpan di folder/{uuid}

        Returns: secure HTTPS URL (dari Cloudinary CDN)
        Raises:  ValueError jika MIME/ukuran tidak valid
        """
        _validate(file, ALLOWED_MIME_IMAGE)

        public_id = f"{folder}/{uuid.uuid4().hex}"

        result = cloudinary.uploader.upload(
            file,
            public_id=public_id,
            resource_type="image",
            overwrite=False,
            # Auto-optimasi: kirim WebP ke browser modern, JPEG ke lama
            eager=[
                {
                    "fetch_format": "auto",
                    "quality": "auto",
                }
            ],
            # Transformasi default saat URL diakses tanpa parameter transformasi
            transformation=[
                {"fetch_format": "auto", "quality": "auto"},
            ],
        )

        url = result.get("secure_url", "")
        logger.info("Cloudinary upload (image) OK → %s", url)
        return url

    # ── Lampiran non-gambar (PDF / DOCX) ─────────────────────────────────────

    @staticmethod
    def upload_attachment(file, folder: str = "pengaduan-lampiran") -> str:
        """
        Upload file lampiran (PDF / DOCX / JPG / PNG) untuk pengaduan.
        Disimpan sebagai resource_type="raw" sehingga Cloudinary tidak
        mencoba memproses sebagai gambar.

        Untuk file JPG/PNG yang dikirim sebagai lampiran, tetap diupload
        sebagai "raw" agar nama file & ekstensi asli terjaga.

        Returns: secure HTTPS URL
        Raises:  ValueError jika MIME/ukuran tidak valid
        """
        _validate(file, ALLOWED_MIME_ATTACHMENT)

        ext = MIME_TO_EXT.get(file.content_type, "")
        public_id = f"{folder}/{uuid.uuid4().hex}.{ext}" if ext else f"{folder}/{uuid.uuid4().hex}"

        result = cloudinary.uploader.upload(
            file,
            public_id=public_id,
            resource_type="raw",
            overwrite=False,
        )

        url = result.get("secure_url", "")
        logger.info("Cloudinary upload (raw) OK → %s", url)
        return url

    # ── Hapus file ────────────────────────────────────────────────────────────

    @staticmethod
    def delete(secure_url: str) -> None:
        """
        Hapus file dari Cloudinary berdasarkan URL-nya.
        Gagal diam-diam (log warning) jika file tidak ditemukan.

        URL Cloudinary format:
          https://res.cloudinary.com/{cloud}/{resource_type}/upload/v{ver}/{public_id}.{ext}
        """
        try:
            resource_type, public_id = _parse_cloudinary_url(secure_url)
            result = cloudinary.uploader.destroy(public_id, resource_type=resource_type)
            if result.get("result") == "ok":
                logger.info("Cloudinary delete OK → %s", public_id)
            else:
                logger.warning("Cloudinary delete tidak berhasil: %s", result)
        except Exception as exc:
            logger.warning("Gagal menghapus file dari Cloudinary: %s — %s", secure_url, exc)


# ─── Helper internal ───────────────────────────────────────────────────────────

def _validate(file, allowed_mimes: set) -> None:
    """
    Validasi MIME type dan ukuran file.
    Raises: ValueError dengan pesan ramah pengguna jika tidak lolos.
    """
    content_type = getattr(file, "content_type", "") or ""

    if content_type not in allowed_mimes:
        raise ValueError(
            f"Tipe file '{content_type}' tidak diizinkan. "
            f"Tipe yang diterima: {', '.join(sorted(allowed_mimes))}"
        )

    size = getattr(file, "size", None)
    if size is not None and size > MAX_SIZE_BYTES:
        raise ValueError(
            f"Ukuran file melebihi batas maksimal 5 MB "
            f"(ukuran saat ini: {size / (1024 * 1024):.2f} MB)."
        )


def _parse_cloudinary_url(url: str) -> tuple[str, str]:
    """
    Parsing URL Cloudinary → (resource_type, public_id).

    Contoh URL image:
      https://res.cloudinary.com/mycloud/image/upload/v1234/berita/abc.jpg
      → ("image", "berita/abc")

    Contoh URL raw:
      https://res.cloudinary.com/mycloud/raw/upload/v1234/pengaduan-lampiran/abc.pdf
      → ("raw", "pengaduan-lampiran/abc.pdf")
    """
    # Deteksi resource type dari segmen URL
    if "/image/upload/" in url:
        resource_type = "image"
        _, rest = url.split("/image/upload/", 1)
    elif "/raw/upload/" in url:
        resource_type = "raw"
        _, rest = url.split("/raw/upload/", 1)
    elif "/video/upload/" in url:
        resource_type = "video"
        _, rest = url.split("/video/upload/", 1)
    else:
        raise ValueError(f"URL Cloudinary tidak dikenali: {url}")

    # Hapus prefix versi (v1234567890/)
    rest = re.sub(r"^v\d+/", "", rest)

    if resource_type == "image":
        # Hapus ekstensi file untuk image (public_id tidak termasuk ekstensi)
        public_id = re.sub(r"\.[a-zA-Z0-9]+$", "", rest)
    else:
        # Untuk raw/video, public_id TERMASUK ekstensi
        public_id = rest

    return resource_type, public_id
