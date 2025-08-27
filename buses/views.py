from django.shortcuts import render, get_object_or_404
from django.views.generic import (
    ListView,
    DetailView,
    TemplateView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from .models import Bus, Seat


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to ensure only admin users can access admin views"""

    def test_func(self):
        return self.request.user.is_authenticated and (
            self.request.user.is_admin or self.request.user.is_staff_member
        )


class BusListView(ListView):
    model = Bus
    template_name = "buses/list.html"
    context_object_name = "buses"

    def get_queryset(self):
        return Bus.objects.filter(is_active=True).order_by("bus_name")


class BusDetailView(DetailView):
    model = Bus
    template_name = "buses/detail.html"
    context_object_name = "bus"


class BusSeatView(TemplateView):
    template_name = "buses/seats.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bus = get_object_or_404(Bus, pk=kwargs["pk"], is_active=True)
        travel_date = self.request.GET.get("date", timezone.now().date())

        context["bus"] = bus
        context["travel_date"] = travel_date
        context["seats"] = self.get_seat_availability(bus, travel_date)
        return context

    def get_seat_availability(self, bus, travel_date):
        """Get seats with availability status"""
        from bookings.models import Booking

        seats = bus.seats.all().order_by("seat_number")
        booked_seats = Booking.objects.filter(
            bus=bus, travel_date__date=travel_date, status__in=["confirmed", "pending"]
        ).values_list("seat_id", flat=True)

        seat_data = []
        for seat in seats:
            seat_data.append(
                {
                    "id": seat.id,
                    "number": seat.seat_number,
                    "is_window": seat.is_window,
                    "is_available": seat.is_available and seat.id not in booked_seats,
                    "is_booked": seat.id in booked_seats,
                }
            )

        return seat_data

    def get(self, request, *args, **kwargs):
        # Handle AJAX requests for seat availability
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            bus = get_object_or_404(Bus, pk=kwargs["pk"], is_active=True)
            travel_date = request.GET.get("date", timezone.now().date())
            seats = self.get_seat_availability(bus, travel_date)
            return JsonResponse({"seats": seats})

        return super().get(request, *args, **kwargs)


def get_bus_seats_ajax(request, bus_id):
    """AJAX endpoint for getting bus seat availability"""
    if request.method == "GET":
        bus = get_object_or_404(Bus, pk=bus_id, is_active=True)
        travel_date = request.GET.get("date", timezone.now().date())

        # Convert string date to date object if needed
        if isinstance(travel_date, str):
            try:
                travel_date = timezone.datetime.strptime(travel_date, "%Y-%m-%d").date()
            except ValueError:
                travel_date = timezone.now().date()

        from bookings.models import Booking

        seats = bus.seats.all().order_by("seat_number")
        booked_seats = Booking.objects.filter(
            bus=bus, travel_date__date=travel_date, status__in=["confirmed", "pending"]
        ).values_list("seat_id", flat=True)

        seat_data = []
        for seat in seats:
            seat_data.append(
                {
                    "id": seat.id,
                    "number": seat.seat_number,
                    "is_window": seat.is_window,
                    "is_available": seat.is_available and seat.id not in booked_seats,
                    "is_booked": seat.id in booked_seats,
                }
            )

        return JsonResponse(
            {
                "success": True,
                "seats": seat_data,
                "bus_name": bus.bus_name,
                "total_seats": bus.total_seats,
            }
        )

    return JsonResponse({"success": False, "error": "Invalid request method"})


class BusCreateView(AdminRequiredMixin, CreateView):
    model = Bus
    template_name = "buses/create.html"
    fields = [
        "bus_number",
        "bus_name",
        "bus_type",
        "seat_capacity",
        "assigned_route",
        "is_active",
    ]
    success_url = reverse_lazy("accounts:admin_manage_buses")

    def form_valid(self, form):
        messages.success(self.request, "Bus created successfully!")
        return super().form_valid(form)


class BusUpdateView(AdminRequiredMixin, UpdateView):
    model = Bus
    template_name = "buses/update.html"
    fields = [
        "bus_number",
        "bus_name",
        "bus_type",
        "seat_capacity",
        "assigned_route",
        "is_active",
    ]
    success_url = reverse_lazy("accounts:admin_manage_buses")

    def form_valid(self, form):
        messages.success(self.request, "Bus updated successfully!")
        return super().form_valid(form)


class BusDeleteView(AdminRequiredMixin, DeleteView):
    model = Bus
    template_name = "buses/confirm_delete.html"
    success_url = reverse_lazy("accounts:admin_manage_buses")
    context_object_name = "bus"

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(
            request, f"Bus {obj.bus_number} has been deleted successfully!"
        )
        return super().delete(request, *args, **kwargs)
