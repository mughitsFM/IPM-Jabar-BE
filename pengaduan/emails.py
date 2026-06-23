"""
pengaduan/emails.py
Notifikasi email untuk modul Pengaduan.

Dua email dikirim saat pengaduan baru masuk:
1. Konfirmasi ke pengirim (PD/PC/PR) bahwa pengaduan diterima
2. Notifikasi ke admin PW IPM Jabar

Dipanggil dari PengaduanService.create() setelah dokumen berhasil disimpan.
"""

import logging
from django.core.mail import send_mail, EmailMessage
from django.conf import settings

logger = logging.getLogger(__name__)


def kirim_konfirmasi_pengirim(email: str, perihal: str, asal_pimpinan: str) -> None:
    """
    Email konfirmasi ke pengirim pengaduan/surat.

    Args:
        email:          Alamat email pengirim
        perihal:        Perihal pengaduan/surat
        asal_pimpinan:  Nama organisasi pengirim (mis. "PD IPM Kab. Bandung")
    """
    subject = f"[PW IPM Jabar] Konfirmasi Penerimaan: {perihal}"
    body = f"""Assalamu'alaikum Warahmatullahi Wabarakatuh,

Terima kasih, pengaduan/pengajuan surat Anda telah kami terima dengan detail sebagai berikut:

- Dari          : {asal_pimpinan} ({email})
- Perihal       : {perihal}
- Status        : Diterima

Tim PW IPM Jawa Barat akan segera menindaklanjuti pengaduan/pengajuan Anda.
Anda akan mendapatkan notifikasi lebih lanjut jika ada perkembangan.

Jika ada pertanyaan, silakan hubungi kami melalui saluran resmi PW IPM Jawa Barat.

Fastabiqul Khairat,
Bidang Teknologi Informasi
Pimpinan Wilayah Ikatan Pelajar Muhammadiyah Jawa Barat
"""
    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        logger.info("Email konfirmasi terkirim ke: %s (perihal: %s)", email, perihal)
    except Exception as exc:
        logger.error("Gagal mengirim email konfirmasi ke %s: %s", email, exc)


def kirim_notifikasi_admin(data: dict) -> None:
    """
    Email notifikasi ke admin PW IPM Jabar saat ada pengaduan baru.

    Args:
        data: dict dengan key email, asal_pimpinan, perihal, isi
    """
    subject = f"[Pengaduan Baru] {data.get('perihal', '-')}"
    body = f"""Ada pengaduan/pengajuan surat baru masuk.

Detail:
- Dari       : {data.get('asal_pimpinan', '-')} ({data.get('email', '-')})
- Perihal    : {data.get('perihal', '-')}
- Isi        :

{data.get('isi', '-')}

---
Silakan login ke panel admin untuk melihat dan menindaklanjuti pengaduan ini.
"""
    try:
        msg = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.ADMIN_NOTIF_EMAIL],
        )
        msg.send(fail_silently=False)
        logger.info(
            "Email notifikasi admin terkirim (perihal: %s, dari: %s)",
            data.get("perihal"),
            data.get("email"),
        )
    except Exception as exc:
        logger.error("Gagal mengirim notifikasi admin: %s", exc)
