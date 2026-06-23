from django.urls import path
from .views import AdminBeritaListCreateView, AdminBeritaDetailView

urlpatterns = [
    path("", AdminBeritaListCreateView.as_view(), name="admin-berita-list-create"),
    path("<str:berita_id>/", AdminBeritaDetailView.as_view(), name="admin-berita-detail"),
]
