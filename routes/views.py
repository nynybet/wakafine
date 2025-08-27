from django.shortcuts import render
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from .models import Route
from .forms import RouteForm, RouteSearchForm


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to ensure only admin users can access admin views"""

    def test_func(self):
        return self.request.user.is_authenticated and (
            self.request.user.is_admin or self.request.user.is_staff_member
        )


class RouteListView(ListView):
    model = Route
    template_name = "routes/list.html"
    context_object_name = "routes"
    paginate_by = 10

    def get_queryset(self):
        return Route.objects.filter(is_active=True).order_by("origin", "departure_time")


class RouteSearchView(ListView):
    model = Route
    template_name = "routes/search.html"
    context_object_name = "routes"

    def get_queryset(self):
        queryset = Route.objects.filter(is_active=True)

        origin = self.request.GET.get("origin")
        destination = self.request.GET.get("destination")
        travel_date = self.request.GET.get("travel_date")

        if origin:
            queryset = queryset.filter(origin=origin)
        if destination:
            queryset = queryset.filter(destination=destination)

        return queryset.order_by("departure_time")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["origin"] = self.request.GET.get("origin", "")
        context["destination"] = self.request.GET.get("destination", "")
        context["travel_date"] = self.request.GET.get("travel_date", "")
        return context


class RouteDetailView(DetailView):
    model = Route
    template_name = "routes/detail.html"
    context_object_name = "route"


class AdminRouteDetailView(AdminRequiredMixin, DetailView):
    model = Route
    template_name = "routes/admin_detail.html"
    context_object_name = "route"


class RouteCreateView(AdminRequiredMixin, CreateView):
    model = Route
    form_class = RouteForm
    template_name = "routes/create.html"
    success_url = reverse_lazy("accounts:admin_manage_routes")

    def form_valid(self, form):
        messages.success(self.request, "Route created successfully!")
        return super().form_valid(form)


class RouteUpdateView(AdminRequiredMixin, UpdateView):
    model = Route
    form_class = RouteForm
    template_name = "routes/update.html"
    success_url = reverse_lazy("accounts:admin_manage_routes")

    def form_valid(self, form):
        messages.success(self.request, "Route updated successfully!")
        return super().form_valid(form)


class RouteDeleteView(AdminRequiredMixin, DeleteView):
    model = Route
    template_name = "routes/confirm_delete.html"
    success_url = reverse_lazy("accounts:admin_manage_routes")
    context_object_name = "route"

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(request, f"Route {obj.name} has been deleted successfully!")
        return super().delete(request, *args, **kwargs)
