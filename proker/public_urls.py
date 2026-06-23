from django.urls import path
from .views import ProkerListView

urlpatterns = [
    path("", ProkerListView.as_view(), name="proker-list"),
]
