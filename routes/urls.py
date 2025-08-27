from django.urls import path
from . import views

app_name = "routes"

urlpatterns = [
    path("", views.RouteListView.as_view(), name="list"),
    path("search/", views.RouteSearchView.as_view(), name="search"),
    path("create/", views.RouteCreateView.as_view(), name="create"),
    path("<int:pk>/", views.RouteDetailView.as_view(), name="detail"),
    path(
        "<int:pk>/admin-detail/",
        views.AdminRouteDetailView.as_view(),
        name="admin_detail",
    ),
    path("<int:pk>/update/", views.RouteUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", views.RouteDeleteView.as_view(), name="delete"),
]
