from django.urls import path
from . import views

urlpatterns = [
    path("", views.inventory_check, name="inventory_check"),
    path(
        "update/<int:entry_id>/",
        views.inventory_update,
        name="inventory_update",
    ),
]
