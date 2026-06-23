from django.urls import path
from .views import (
    AdminPengaduanListView,
    AdminPengaduanDetailView,
    AdminPengaduanStatusView,
)

urlpatterns = [
    path("", AdminPengaduanListView.as_view(), name="admin-pengaduan-list"),
    path("<str:pengaduan_id>/", AdminPengaduanDetailView.as_view(), name="admin-pengaduan-detail"),
    path("<str:pengaduan_id>/status/", AdminPengaduanStatusView.as_view(), name="admin-pengaduan-status"),
]
