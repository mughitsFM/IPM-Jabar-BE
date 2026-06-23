from django.urls import path
from .views import PengaduanCreateView

urlpatterns = [
    path("", PengaduanCreateView.as_view(), name="pengaduan-create"),
]
