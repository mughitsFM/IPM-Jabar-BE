# Backend — PW IPM Jawa Barat

**Django + Django REST Framework · Cloud Firestore · Firebase Authentication**

---

## Struktur Proyek

```
backend/
├── config/                  # Konfigurasi Django (settings, URLs, WSGI)
│   └── settings/
│       ├── base.py          # Setting bersama
│       ├── dev.py           # Development lokal
│       └── prod.py          # Production (VPS)
├── core/                    # Infrastruktur lintas-app
│   ├── firebase_client.py   # Init Firebase Admin SDK
│   ├── authentication.py    # FirebaseAuthentication DRF
│   ├── permissions.py       # IsAdminUser, IsSuperAdmin
│   ├── responses.py         # Format response standar
│   ├── exceptions.py        # Global exception handler
│   └── pagination.py        # Helper pagination Firestore
├── accounts/                # Autentikasi & manajemen admin
├── berita/                  # Modul Berita & Informasi
├── profil/                  # Modul Profil Kepengurusan
├── proker/                  # Modul Program Kerja / Kalender
├── pengaduan/               # Modul Pengaduan & Pengajuan Surat
├── storage_files/           # Upload file ke Firebase Storage
├── scripts/                 # Script utilitas
├── firestore.indexes.json   # Composite index Firestore
├── firestore.rules          # Security Rules Firestore
├── .env.example             # Template environment variables
└── requirements.txt
```

---

## Prasyarat

- Python 3.11+
- Akun Firebase (project sudah dibuat, Firestore & Storage diaktifkan)
- Service account JSON dari Firebase Console

---

## Cara Setup (Development)

### 1. Clone & buat virtual environment

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Konfigurasi environment

```bash
cp .env.example .env
# Buka .env dan isi semua nilai yang diperlukan
```

Field wajib di `.env`:
| Field | Keterangan |
|---|---|
| `DJANGO_SECRET_KEY` | Secret key Django (buat acak, min. 50 karakter) |
| `FIREBASE_SERVICE_ACCOUNT_PATH` | Path ke file `.json` service account |
| `CLOUDINARY_CLOUD_NAME` | Nama cloud Cloudinary (dari Dashboard) |
| `CLOUDINARY_API_KEY` | API Key Cloudinary |
| `CLOUDINARY_API_SECRET` | API Secret Cloudinary |

### 3. Taruh service account JSON

Simpan file service account JSON dari Firebase Console ke lokasi yang sudah diisi
di `FIREBASE_SERVICE_ACCOUNT_PATH`. Pastikan file ini **tidak masuk ke Git**.

```bash
# Contoh:
mkdir -p secrets
mv ~/Downloads/firebase-adminsdk-xxx.json secrets/firebase-service-account.json
```

### 4. Setup Cloudinary

1. Daftar gratis di [cloudinary.com](https://cloudinary.com/users/register_free)
2. Buka **Dashboard → API Keys**
3. Isi `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, dan `CLOUDINARY_API_SECRET` di `.env`

> **Kelebihan Cloudinary vs Firebase Storage:**
> - Free tier 25 GB (Firebase Storage hanya 5 GB)
> - CDN global otomatis tanpa konfigurasi tambahan
> - Auto-konversi ke WebP & `quality:auto` → hemat bandwidth ~30%

### 4b. Cek koneksi Firebase & Cloudinary

```bash
python scripts/check_firebase.py
```

Script ini mengecek Firestore, Cloudinary, dan Firebase Auth sekaligus.
Semua indikator harus OK sebelum lanjut.

### 5. Deploy Firestore indexes & rules

```bash
# Install Firebase CLI jika belum ada
npm install -g firebase-tools
firebase login
firebase use <project-id>

firebase deploy --only firestore:indexes
firebase deploy --only firestore:rules
```

### 6. Buat akun Super Admin pertama

```bash
python scripts/create_superadmin.py
```

### 7. Jalankan server development

```bash
python manage.py runserver
# Server berjalan di http://127.0.0.1:8000
```

---

## Ringkasan Endpoint API

| Method | Endpoint | Auth | Keterangan |
|---|---|---|---|
| POST | `/api/auth/session` | Token | Verifikasi login, ambil profil admin |
| GET | `/api/berita/` | Public | Daftar berita terpublikasi |
| GET | `/api/berita/<slug>/` | Public | Detail berita |
| GET | `/api/profil/` | Public | Daftar profil kepengurusan |
| GET | `/api/proker/` | Public | Daftar program kerja |
| POST | `/api/pengaduan/` | Public | Kirim pengaduan/surat |
| GET/POST | `/api/admin/berita/` | Admin | Kelola berita |
| PUT/DELETE | `/api/admin/berita/<id>/` | Admin | Update/hapus berita |
| GET/POST | `/api/admin/profil/` | Admin | Kelola profil |
| PUT/DELETE | `/api/admin/profil/<id>/` | Admin | Update/hapus profil |
| GET/POST | `/api/admin/proker/` | Admin | Kelola proker |
| PUT/DELETE | `/api/admin/proker/<id>/` | Admin | Update/hapus proker |
| GET | `/api/admin/pengaduan/` | Admin | Daftar pengaduan |
| GET | `/api/admin/pengaduan/<id>/` | Admin | Detail pengaduan |
| PATCH | `/api/admin/pengaduan/<id>/status/` | Admin | Ubah status |
| GET/POST | `/api/admin/pengguna/` | Super Admin | Kelola akun admin |
| PATCH | `/api/admin/pengguna/<uid>/` | Super Admin | Update role/status |
| GET | `/api/admin/dashboard/summary/` | Admin | Ringkasan dashboard |

### Format Response Standar

```json
{
  "status": "success",
  "message": "Deskripsi singkat hasil",
  "data": { },
  "errors": null
}
```

Error response:
```json
{
  "status": "error",
  "message": "Pesan error",
  "data": null,
  "errors": { "field": ["pesan validasi"] }
}
```

---

## Deploy ke Production (VPS)

### 1. Siapkan server

```bash
# Install Python, pip, nginx, gunicorn
sudo apt update && sudo apt install python3.11 python3.11-venv nginx -y
```

### 2. Upload kode & setup

```bash
git clone <repo-url> /var/www/ipmjabar-backend
cd /var/www/ipmjabar-backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env untuk production
```

### 3. Jalankan dengan Gunicorn (systemd service)

Buat file `/etc/systemd/system/ipmjabar-backend.service`:

```ini
[Unit]
Description=PW IPM Jabar Django Backend
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/ipmjabar-backend
EnvironmentFile=/var/www/ipmjabar-backend/.env
Environment=DJANGO_SETTINGS_MODULE=config.settings.prod
ExecStart=/var/www/ipmjabar-backend/venv/bin/gunicorn \
    config.wsgi:application \
    --bind 127.0.0.1:8000 \
    --workers 3 \
    --timeout 60
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable ipmjabar-backend
sudo systemctl start ipmjabar-backend
```

### 4. Nginx sebagai reverse proxy

```nginx
server {
    listen 443 ssl;
    server_name api.ipmjabar.or.id;

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        client_max_body_size 6M;   # Sedikit di atas batas 5MB upload
    }
}
```

---

## Keamanan

| Ancaman | Mitigasi yang diterapkan |
|---|---|
| Token palsu | ID Token diverifikasi Firebase Admin SDK setiap request |
| Privilege escalation | Role dibaca dari custom claims (server-side), bukan dari body request |
| XSS via rich-text | Konten HTML disanitasi `bleach` sebelum disimpan ke Firestore |
| File berbahaya | Validasi MIME type + batas ukuran 5 MB sebelum dikirim ke Cloudinary |
| Path traversal | Nama file di-generate UUID, tidak memakai nama asli dari client |
| Akses DB langsung | Firestore Security Rules menolak semua akses dari Client SDK |
| Secret bocor | `.env` + service account JSON di `.gitignore` |
| Kredensial Cloudinary | `API_KEY` & `API_SECRET` hanya ada di `.env` server, tidak pernah ke client |

---

*Fastabiqul Khairat — PW IPM Jawa Barat 2025*
