from datetime import datetime
from multiprocessing import context
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import (
    LoginView as BaseLoginView,
    LogoutView as BaseLogoutView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, TemplateView, UpdateView
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
from .models import User
from .forms import CustomUserCreationForm, UserProfileForm, CustomPasswordChangeForm


class LoginView(BaseLoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(
            self.request,
            f"Welcome back, {form.get_user().get_full_name() or form.get_user().username}!",
        )
        return super().form_valid(form)


class LogoutView(BaseLogoutView):
    next_page = reverse_lazy("home")  # Redirect to home page after logout
    http_method_names = ["get", "post"]  # Allow both GET and POST requests

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, "You have been logged out successfully.")
        return super().dispatch(request, *args, **kwargs)


class RegisterView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("accounts:login")

    def form_valid(self, form):
        user = form.save()
        messages.success(
            self.request, "Account created successfully! You can now log in."
        )
        return super().form_valid(form)


class DashboardView(LoginRequiredMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        # Redirect admin and staff to the custom admin panel
        if request.user.is_admin or request.user.is_staff_member:
            return redirect("accounts:admin_dashboard")
        return super().get(request, *args, **kwargs)

    def get_template_names(self):
        if self.request.user.is_admin:
            return ["accounts/admin_dashboard.html"]
        elif self.request.user.is_staff_member:
            return ["accounts/staff_dashboard.html"]
        else:
            return ["accounts/customer_dashboard.html"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_customer:
            from bookings.models import Booking

            context["recent_bookings"] = Booking.objects.filter(customer=user).order_by(
                "-created_at"
            )[:5]
            context["total_bookings"] = Booking.objects.filter(customer=user).count()
            context["pending_bookings"] = Booking.objects.filter(
                customer=user, status="pending"
            ).count()

        elif user.is_admin:
            from bookings.models import Booking
            from routes.models import Route
            from buses.models import Bus
            from django.db.models import Sum, Count
            from django.utils import timezone

            today = timezone.now().date()
            context["total_bookings"] = Booking.objects.count()
            context["today_bookings"] = Booking.objects.filter(
                travel_date__date=today
            ).count()
            context["total_revenue"] = (
                Booking.objects.filter(status="confirmed").aggregate(
                    Sum("amount_paid")
                )["amount_paid__sum"]
                or 0
            )
            context["active_routes"] = Route.objects.filter(is_active=True).count()
            context["active_buses"] = Bus.objects.filter(is_active=True).count()
            context["recent_bookings"] = Booking.objects.order_by("-created_at")[:10]
            today = datetime.now().date()
            month_start = today.replace(day=1)
            last_30 = today - datetime.timedelta(days=30)

        # --- KPI cards ---
            context["kpis"] = {
            "total_bookings_today": Booking.objects.filter(travel_date__date=today).count(),
            "total_bookings_month": Booking.objects.filter(travel_date__date__gte=month_start).count(),
            "total_revenue_today": Booking.objects.filter(travel_date__date=today)
                                .aggregate(Sum("amount_paid"))["amount_paid__sum"] or 0,
            "total_revenue_month": Booking.objects.filter(travel_date__date__gte=month_start)
                                .aggregate(Sum("amount_paid"))["amount_paid__sum"] or 0,
            "active_routes": Route.objects.count(),
            "total_vehicles": Bus.objects.count(),
        }

        # --- Chart: Bookings over time (last 30 days) ---
            bookings_qs = (
            Booking.objects.filter(travel_date__date__gte=last_30)
            .extra(select={"day": "date(travel_date)"})
            .values("day")
            .annotate(c=Count("id"))
            .order_by("day")
        )
            context["bookings_over_time"] = {
            "labels": [b["day"] for b in bookings_qs],
            "data": [b["c"] for b in bookings_qs],
        }

        # --- Chart: Revenue by route (top 10) ---
            revenue_qs = (
            Booking.objects.values("route__destination")
            .annotate(total=Sum("amount_paid"))
            .order_by("-total")[:10]
        )
            context["revenue_by_route"] = {
            "labels": [r["route__destination"] for r in revenue_qs],
            "data": [r["total"] or 0 for r in revenue_qs],
        }

        # --- Chart: Popular routes (by bookings, top 10) ---
            popular_qs = (
            Booking.objects.values("route__destination")
            .annotate(c=Count("id"))
            .order_by("-c")[:10]
        )
            context["popular_routes"] = {
            "labels": [r["route__destination"] for r in popular_qs],
            "data": [r["c"] for r in popular_qs],
        }

        # --- Bus-related charts ---
            buses = Bus.objects.all()

        # Vehicle Utilization (trips per bus)
            vehicle_util_qs = (
            Booking.objects.values("bus__bus_name")
            .annotate(trips=Count("id"))
            .order_by("-trips")
        )
            context["vehicle_utilization"] = {
            "labels": [v["bus__bus_name"] for v in vehicle_util_qs],
            "data": [v["trips"] for v in vehicle_util_qs],
        }
        # --- Chart: Bookings per Bus (last 30 days, confirmed only) ---
            bus_labels = []
            bus_data = []
            for bus in buses:
                bookings_count = Booking.objects.filter(
                bus=bus,
                travel_date__date__gte=last_30,
                status="confirmed"  # Only confirmed bookings
                ).count()
                bus_labels.append(f"{bus.bus_name} ({bus.bus_number})")
                bus_data.append(bookings_count)

            context["bookings_per_bus"] = {"labels": bus_labels, "data": bus_data}

# --- Chart: Available seats per Bus today ---
            bus_labels_seats = []
            available_seats_data = []
            for bus in buses:
                bus_labels_seats.append(f"{bus.bus_name} ({bus.bus_number})")
    # Use the property which already filters by confirmed bookings
                available_seats_data.append(bus.available_seats)

            context["available_seats_per_bus"] = {"labels": bus_labels_seats, "data": available_seats_data}
        elif user.is_staff_member:
            from bookings.models import Booking
            from django.utils import timezone

            context["today_bookings"] = Booking.objects.filter(
                travel_date__date=timezone.now().date()
            )
            context["pending_validations"] = Booking.objects.filter(
                status="pending"
            ).count()

        return context


class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = "accounts/profile.html"
    success_url = reverse_lazy("accounts:profile")

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["password_form"] = CustomPasswordChangeForm(user=self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        # Check if this is a password change request
        if "change_password" in request.POST:
            password_form = CustomPasswordChangeForm(
                user=request.user, data=request.POST
            )
            if password_form.is_valid():
                password_form.save()
                messages.success(request, "Password changed successfully!")
                return redirect("accounts:profile")
            else:
                # Return with password form errors
                self.object = self.get_object()
                profile_form = self.get_form()
                return self.render_to_response(
                    self.get_context_data(
                        form=profile_form, password_form=password_form
                    )
                )
        else:
            # Handle profile update
            return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "Profile updated successfully!")
        return super().form_valid(form)
