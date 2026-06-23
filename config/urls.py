"""
config/urls.py
Root URL configuration.
Semua route dikelompokkan di bawah /api/ sesuai spesifikasi BAB 4.4.
"""

from django.urls import path, include

urlpatterns = [
    path(
        "api/",
        include([
            # ── Autentikasi ──────────────────────────────────────────────
            # POST /api/auth/session
            path("auth/", include("accounts.auth_urls")),

            # ── Public Endpoints ─────────────────────────────────────────
            # GET  /api/berita/               → daftar berita terpublikasi
            # GET  /api/berita/<slug>/         → detail berita
            path("berita/", include("berita.public_urls")),

            # GET  /api/profil/               → daftar profil kepengurusan
            path("profil/", include("profil.public_urls")),

            # GET  /api/proker/               → daftar proker (filter bulan/bidang)
            path("proker/", include("proker.public_urls")),

            # POST /api/pengaduan/             → kirim pengaduan/surat
            path("pengaduan/", include("pengaduan.public_urls")),

            # ── Admin Endpoints (wajib Bearer Token) ─────────────────────
            path(
                "admin/",
                include([
                    # POST/GET   /api/admin/berita/
                    # PUT/DELETE /api/admin/berita/<id>/
                    path("berita/", include("berita.admin_urls")),

                    # POST/GET   /api/admin/profil/
                    # PUT/DELETE /api/admin/profil/<id>/
                    path("profil/", include("profil.admin_urls")),

                    # POST/GET   /api/admin/proker/
                    # PUT/DELETE /api/admin/proker/<id>/
                    path("proker/", include("proker.admin_urls")),

                    # GET    /api/admin/pengaduan/
                    # GET    /api/admin/pengaduan/<id>/
                    # PATCH  /api/admin/pengaduan/<id>/status/
                    path("pengaduan/", include("pengaduan.admin_urls")),

                    # GET/POST  /api/admin/pengguna/
                    # PATCH     /api/admin/pengguna/<uid>/
                    path("pengguna/", include("accounts.admin_urls")),

                    # GET /api/admin/dashboard/summary/
                    path("dashboard/", include("accounts.dashboard_urls")),
                ]),
            ),
        ]),
    ),
]
