from django.urls import path
from .views import AdminProfilListCreateView, AdminProfilDetailView

urlpatterns = [
    path("", AdminProfilListCreateView.as_view(), name="admin-profil-list-create"),
    path("<str:profil_id>/", AdminProfilDetailView.as_view(), name="admin-profil-detail"),
]
