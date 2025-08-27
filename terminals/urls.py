from django.urls import path
from . import views

app_name = "terminals"

urlpatterns = [
    # Public terminal views
    path("", views.TerminalListView.as_view(), name="list"),
    path("<int:pk>/", views.TerminalDetailView.as_view(), name="detail"),
    # Admin CRUD views
    path("create/", views.TerminalCreateView.as_view(), name="create"),
    path("<int:pk>/edit/", views.TerminalUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", views.TerminalDeleteView.as_view(), name="delete"),
]
