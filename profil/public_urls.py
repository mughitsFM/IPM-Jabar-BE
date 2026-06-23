from django.urls import path
from .views import ProfilListView

urlpatterns = [
    path("", ProfilListView.as_view(), name="profil-list"),
]
