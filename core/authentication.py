"""
core/authentication.py
Custom DRF Authentication Backend berbasis Firebase ID Token.

Alur:
1. Ambil header Authorization: Bearer <id_token>
2. Verifikasi ID Token via Firebase Admin SDK (server-side)
3. Baca custom claim `role` dari decoded token
4. Return objek FirebaseUser yang dipakai di `request.user`

Keamanan:
- Token diverifikasi setiap request (tidak ada session lokal)
- Role dibaca dari custom claims yang diset server-side (bukan dari body request)
- Tidak bisa di-spoof karena verified oleh Firebase Auth
"""

from firebase_admin import auth as firebase_auth
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class FirebaseUser:
    """
    Representasi user yang sudah terautentikasi via Firebase.
    Disimpan di `request.user` oleh DRF setelah autentikasi berhasil.
    """

    is_authenticated = True
    is_anonymous = False

    def __init__(self, decoded_token: dict):
        self.uid: str = decoded_token["uid"]
        self.email: str = decoded_token.get("email", "")
        # `role` berasal dari Firebase custom claims yang di-set via Admin SDK
        # Default "editor" agar tidak ada elevasi privilege tak terduga
        self.role: str = decoded_token.get("role", "editor")

    def __str__(self) -> str:
        return f"FirebaseUser(uid={self.uid}, role={self.role})"


class FirebaseAuthentication(BaseAuthentication):
    """
    DRF Authentication class.
    Dipasang di DEFAULT_AUTHENTICATION_CLASSES pada settings.py.

    View publik (tidak butuh auth) tetap perlu mendeclare:
        authentication_classes = []
        permission_classes = [AllowAny]
    agar DRF tidak mencoba parsing token pada setiap request.
    """

    def authenticate(self, request):
        """
        Return (FirebaseUser, None) jika token valid,
        atau None jika tidak ada Authorization header (DRF akan lanjut ke next auth class),
        atau raise AuthenticationFailed jika token ada tapi tidak valid.
        """
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            # Tidak ada token → lewati (endpoint publik masih bisa diakses)
            return None

        id_token = auth_header.split(" ", 1)[1].strip()
        if not id_token:
            return None

        try:
            decoded_token = firebase_auth.verify_id_token(id_token)
        except firebase_auth.ExpiredIdTokenError:
            raise AuthenticationFailed("Token sudah kedaluwarsa. Silakan login ulang.")
        except firebase_auth.InvalidIdTokenError:
            raise AuthenticationFailed("Token tidak valid.")
        except Exception:
            raise AuthenticationFailed("Gagal memverifikasi token. Coba lagi.")

        return (FirebaseUser(decoded_token), None)

    def authenticate_header(self, request):
        return "Bearer"
