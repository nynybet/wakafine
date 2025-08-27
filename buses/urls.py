from django.urls import path
from . import views

app_name = "buses"

urlpatterns = [
    path("", views.BusListView.as_view(), name="list"),
    path("create/", views.BusCreateView.as_view(), name="create"),
    path("<int:pk>/", views.BusDetailView.as_view(), name="detail"),
    path("<int:pk>/update/", views.BusUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", views.BusDeleteView.as_view(), name="delete"),
    path("<int:pk>/seats/", views.BusSeatView.as_view(), name="seats"),
    path("ajax/seats/<int:bus_id>/", views.get_bus_seats_ajax, name="ajax_seats"),
]
