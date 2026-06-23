from django.urls import path
from .views import AdminProkerListCreateView, AdminProkerDetailView

urlpatterns = [
    path("", AdminProkerListCreateView.as_view(), name="admin-proker-list-create"),
    path("<str:proker_id>/", AdminProkerDetailView.as_view(), name="admin-proker-detail"),
]
