from django.urls import path
from .views import AdminPenggunaListCreateView, AdminPenggunaUpdateView

urlpatterns = [
    path("", AdminPenggunaListCreateView.as_view(), name="admin-pengguna-list-create"),
    path("<str:uid>/", AdminPenggunaUpdateView.as_view(), name="admin-pengguna-update"),
]
