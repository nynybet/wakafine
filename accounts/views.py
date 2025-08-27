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
