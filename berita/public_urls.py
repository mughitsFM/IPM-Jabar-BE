from django.urls import path
from .views import BeritaListView, BeritaDetailView

urlpatterns = [
    path("", BeritaListView.as_view(), name="berita-list"),
    path("<str:slug>/", BeritaDetailView.as_view(), name="berita-detail"),
]
