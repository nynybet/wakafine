from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView,
)
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q, Sum, Count
from django.utils import timezone
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.template.loader import render_to_string

from .models import User
from .forms import AdminUserCreateForm, AdminUserEditForm
from buses.models import Bus
from routes.models import Route
from bookings.models import Booking
from terminals.models import Terminal


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to ensure only admin users can access admin views"""

    def test_func(self):
        return self.request.user.is_authenticated and (
            self.request.user.is_admin or self.request.user.is_staff_member
        )


class AdminDashboardView(AdminRequiredMixin, TemplateView):
    template_name = "accounts/admin/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Dashboard statistics
        today = timezone.now().date()
        context.update(
            {
                "total_bookings": Booking.objects.count(),
                "today_bookings": Booking.objects.filter(
                    travel_date__date=today
                ).count(),
                "total_revenue": Booking.objects.filter(status="confirmed").aggregate(
                    total=Sum("amount_paid")
                )["total"]
                or 0,
                "active_routes": Route.objects.filter(is_active=True).count(),
                "active_buses": Bus.objects.filter(is_active=True).count(),
                "active_terminals": Terminal.objects.filter(is_active=True).count(),
                "total_users": User.objects.count(),
                "pending_bookings": Booking.objects.filter(status="pending").count(),
                "recent_bookings": Booking.objects.select_related(
                    "customer", "bus__assigned_route"
                ).order_by("-created_at")[:10],
            }
        )

        return context


class ManageUsersView(AdminRequiredMixin, ListView):
    model = User
    template_name = "accounts/admin/manage_users.html"
    context_object_name = "users"
    paginate_by = 20

    def get_queryset(self):
        queryset = User.objects.all().order_by("-date_joined")
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search)
                | Q(email__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "")
        return context


class ManageRoutesView(AdminRequiredMixin, ListView):
    model = Route
    template_name = "accounts/admin/manage_routes.html"
    context_object_name = "routes"
    paginate_by = 20

    def get_queryset(self):
        return Route.objects.all().order_by("-created_at")


class ManageBusesView(AdminRequiredMixin, ListView):
    model = Bus
    template_name = "accounts/admin/manage_buses.html"
    context_object_name = "buses"
    paginate_by = 20

    def get_queryset(self):
        return (
            Bus.objects.select_related("assigned_route").all().order_by("-created_at")
        )


class ManageBookingsView(AdminRequiredMixin, ListView):
    model = Booking
    template_name = "accounts/admin/manage_bookings.html"
    context_object_name = "bookings"
    paginate_by = 20

    def get_queryset(self):
        queryset = Booking.objects.select_related(
            "customer", "bus__assigned_route"
        ).order_by("-created_at")
        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_filter"] = self.request.GET.get("status", "")
        context["booking_statuses"] = Booking.STATUS_CHOICES
        return context


class ManageTicketsView(AdminRequiredMixin, ListView):
    model = Booking
    template_name = "accounts/admin/manage_tickets.html"
    context_object_name = "tickets"
    paginate_by = 20

    def get_queryset(self):
        # Only show confirmed bookings as tickets
        queryset = (
            Booking.objects.filter(status="confirmed")
            .select_related("customer", "bus__assigned_route")
            .order_by("-created_at")
        )

        # Handle filtering parameters
        search = self.request.GET.get("search")
        status_filter = self.request.GET.get("status")
        date_filter = self.request.GET.get("date")

        if search:
            queryset = queryset.filter(
                Q(pnr_code__icontains=search)
                | Q(customer__first_name__icontains=search)
                | Q(customer__last_name__icontains=search)
                | Q(customer__email__icontains=search)
            )

        # Filter by status type (recent, etc.)
        if status_filter == "recent":
            # Show tickets from last 7 days
            from django.utils import timezone
            from datetime import timedelta

            recent_date = timezone.now().date() - timedelta(days=7)
            queryset = queryset.filter(created_at__date__gte=recent_date)

        # Filter by date (today, etc.)
        if date_filter == "today":
            from django.utils import timezone

            today = timezone.now().date()
            queryset = queryset.filter(travel_date__date=today)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "")
        context["status_filter"] = self.request.GET.get("status", "")
        context["date_filter"] = self.request.GET.get("date", "")
        return context


class ManageTerminalsView(AdminRequiredMixin, ListView):
    model = Terminal
    template_name = "accounts/admin/manage_terminals.html"
    context_object_name = "terminals"
    paginate_by = 20

    def get_queryset(self):
        queryset = Terminal.objects.all().order_by("-created_at")
        search = self.request.GET.get("search")
        terminal_type = self.request.GET.get("type")

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(location__icontains=search)
                | Q(city__icontains=search)
            )

        if terminal_type:
            queryset = queryset.filter(terminal_type=terminal_type)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "")
        context["type_filter"] = self.request.GET.get("type", "")
        context["terminal_types"] = Terminal.TERMINAL_TYPE_CHOICES
        return context


class ToggleUserStatusView(AdminRequiredMixin, TemplateView):
    def post(self, request, *args, **kwargs):
        user_id = kwargs.get("user_id")
        user = get_object_or_404(User, id=user_id)

        user.is_active = not user.is_active
        user.save()

        status = "activated" if user.is_active else "deactivated"
        messages.success(request, f"User {user.username} has been {status}.")

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"status": "success", "is_active": user.is_active})

        return redirect("accounts:admin_manage_users")


class ToggleRouteStatusView(AdminRequiredMixin, TemplateView):
    def post(self, request, *args, **kwargs):
        route_id = kwargs.get("route_id")
        route = get_object_or_404(Route, id=route_id)

        route.is_active = not route.is_active
        route.save()

        status = "activated" if route.is_active else "deactivated"
        messages.success(request, f"Route has been {status}.")

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"status": "success", "is_active": route.is_active})

        return redirect("accounts:admin_manage_routes")


class ToggleBusStatusView(AdminRequiredMixin, TemplateView):
    def post(self, request, *args, **kwargs):
        bus_id = kwargs.get("bus_id")
        bus = get_object_or_404(Bus, id=bus_id)

        bus.is_active = not bus.is_active
        bus.save()

        status = "activated" if bus.is_active else "deactivated"
        messages.success(request, f"Bus {bus.bus_number} has been {status}.")

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"status": "success", "is_active": bus.is_active})

        return redirect("accounts:admin_manage_buses")


class ToggleTerminalStatusView(AdminRequiredMixin, TemplateView):
    def post(self, request, *args, **kwargs):
        terminal_id = kwargs.get("terminal_id")
        terminal = get_object_or_404(Terminal, id=terminal_id)

        terminal.is_active = not terminal.is_active
        terminal.save()

        status = "activated" if terminal.is_active else "deactivated"
        messages.success(request, f"Terminal {terminal.name} has been {status}.")

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"status": "success", "is_active": terminal.is_active})

        return redirect("accounts:admin_manage_terminals")


class UpdateBookingStatusView(AdminRequiredMixin, TemplateView):
    def post(self, request, *args, **kwargs):
        booking_id = kwargs.get("booking_id")
        booking = get_object_or_404(Booking, id=booking_id)
        new_status = request.POST.get("status")

        if new_status in dict(Booking.STATUS_CHOICES):
            booking.status = new_status
            booking.save()

            messages.success(
                request,
                f"Booking {booking.pnr_code} status updated to {booking.get_status_display()}.",
            )

            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse(
                    {"status": "success", "new_status": booking.get_status_display()}
                )

        return redirect("accounts:admin_manage_bookings")


class DeleteUserView(AdminRequiredMixin, DeleteView):
    model = User
    template_name = "accounts/admin/confirm_delete.html"
    success_url = reverse_lazy("accounts:admin_manage_users")
    context_object_name = "object"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object_type"] = "User"
        context["object_name"] = self.object.username
        return context

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(request, f"User {obj.username} has been deleted successfully.")
        return super().delete(request, *args, **kwargs)


class DeleteRouteView(AdminRequiredMixin, DeleteView):
    model = Route
    template_name = "accounts/admin/confirm_delete.html"
    success_url = reverse_lazy("accounts:admin_manage_routes")
    context_object_name = "object"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object_type"] = "Route"
        context["object_name"] = (
            f"{self.object.departure_city} to {self.object.arrival_city}"
        )
        return context

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(
            request,
            f"Route {obj.departure_city} to {obj.arrival_city} has been deleted successfully.",
        )
        return super().delete(request, *args, **kwargs)


class DeleteBusView(AdminRequiredMixin, DeleteView):
    model = Bus
    template_name = "accounts/admin/confirm_delete.html"
    success_url = reverse_lazy("accounts:admin_manage_buses")
    context_object_name = "object"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object_type"] = "Bus"
        context["object_name"] = self.object.bus_number
        return context

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(
            request, f"Bus {obj.bus_number} has been deleted successfully."
        )
        return super().delete(request, *args, **kwargs)


class DeleteBookingView(AdminRequiredMixin, DeleteView):
    model = Booking
    template_name = "accounts/admin/confirm_delete.html"
    success_url = reverse_lazy("accounts:admin_manage_bookings")
    context_object_name = "object"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object_type"] = "Booking"
        context["object_name"] = self.object.pnr_code
        return context

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(
            request, f"Booking {obj.pnr_code} has been deleted successfully."
        )
        return super().delete(request, *args, **kwargs)


class DeleteTerminalView(AdminRequiredMixin, DeleteView):
    model = Terminal
    template_name = "accounts/admin/confirm_delete.html"
    success_url = reverse_lazy("accounts:admin_manage_terminals")
    context_object_name = "object"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object_type"] = "Terminal"
        context["object_name"] = self.object.name
        return context

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(request, f"Terminal {obj.name} has been deleted successfully.")
        return super().delete(request, *args, **kwargs)


# Modal-based AJAX views for user management
class UserDetailModalView(AdminRequiredMixin, TemplateView):
    """AJAX view to get user details for modal display"""

    def get(self, request, *args, **kwargs):
        user_id = kwargs.get("user_id")
        user = get_object_or_404(User, id=user_id)

        context = {
            "user": user,
        }

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            html = render_to_string(
                "accounts/admin/modals/user_detail_modal.html", context, request=request
            )
            return JsonResponse({"html": html})

        return JsonResponse({"error": "Invalid request"}, status=400)


class UserCreateModalView(AdminRequiredMixin, TemplateView):
    """AJAX view for user creation modal"""

    def get(self, request, *args, **kwargs):
        form = AdminUserCreateForm(current_user=request.user)
        context = {"form": form}

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            html = render_to_string(
                "accounts/admin/modals/user_create_modal.html", context, request=request
            )
            return JsonResponse({"html": html})

        return JsonResponse({"error": "Invalid request"}, status=400)

    def post(self, request, *args, **kwargs):
        form = AdminUserCreateForm(request.POST, current_user=request.user)

        if form.is_valid():
            user = form.save()
            messages.success(
                request, f'User "{user.username}" has been created successfully.'
            )

            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse(
                    {
                        "success": True,
                        "message": f'User "{user.username}" has been created successfully.',
                        "redirect_url": reverse_lazy("accounts:admin_manage_users"),
                    }
                )

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            context = {"form": form}
            html = render_to_string(
                "accounts/admin/modals/user_create_modal.html", context, request=request
            )
            return JsonResponse({"html": html, "success": False})

        return JsonResponse({"error": "Invalid request"}, status=400)


class UserEditModalView(AdminRequiredMixin, TemplateView):
    """AJAX view for user editing modal"""

    def get(self, request, *args, **kwargs):
        user_id = kwargs.get("user_id")
        user = get_object_or_404(User, id=user_id)
        form = AdminUserEditForm(instance=user)

        context = {
            "form": form,
            "user": user,
        }

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            html = render_to_string(
                "accounts/admin/modals/user_edit_modal.html", context, request=request
            )
            return JsonResponse({"html": html})

        return JsonResponse({"error": "Invalid request"}, status=400)

    def post(self, request, *args, **kwargs):
        user_id = kwargs.get("user_id")
        user = get_object_or_404(User, id=user_id)
        form = AdminUserEditForm(request.POST, instance=user)

        if form.is_valid():
            user = form.save()
            messages.success(
                request, f'User "{user.username}" has been updated successfully.'
            )

            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse(
                    {
                        "success": True,
                        "message": f'User "{user.username}" has been updated successfully.',
                        "redirect_url": reverse_lazy("accounts:admin_manage_users"),
                    }
                )

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            context = {
                "form": form,
                "user": user,
            }
            html = render_to_string(
                "accounts/admin/modals/user_edit_modal.html", context, request=request
            )
            return JsonResponse({"html": html, "success": False})

        return JsonResponse({"error": "Invalid request"}, status=400)


class UserDeleteModalView(AdminRequiredMixin, TemplateView):
    """AJAX view for user deletion confirmation modal"""

    def get(self, request, *args, **kwargs):
        user_id = kwargs.get("user_id")
        user = get_object_or_404(User, id=user_id)

        context = {
            "user": user,
        }

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            html = render_to_string(
                "accounts/admin/modals/user_delete_modal.html", context, request=request
            )
            return JsonResponse({"html": html})

        return JsonResponse({"error": "Invalid request"}, status=400)

    def post(self, request, *args, **kwargs):
        user_id = kwargs.get("user_id")
        user = get_object_or_404(User, id=user_id)
        username = user.username

        # Prevent deletion of current user
        if user == request.user:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse(
                    {
                        "success": False,
                        "error": "You cannot delete your own account.",
                    }
                )

        user.delete()
        messages.success(request, f'User "{username}" has been deleted successfully.')

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(
                {
                    "success": True,
                    "message": f'User "{username}" has been deleted successfully.',
                    "redirect_url": reverse_lazy("accounts:admin_manage_users"),
                }
            )

        return JsonResponse({"error": "Invalid request"}, status=400)


class TicketQuickStatsAPIView(AdminRequiredMixin, TemplateView):
    """API endpoint for quick ticket stats"""

    def get(self, request, *args, **kwargs):
        from django.utils import timezone
        from datetime import timedelta

        today = timezone.now().date()

        # Active tickets count (confirmed bookings)
        active_tickets = Booking.objects.filter(status="confirmed").count()

        # Today's revenue from confirmed bookings
        today_revenue = (
            Booking.objects.filter(
                status="confirmed", travel_date__date=today
            ).aggregate(total=Sum("amount_paid"))["total"]
            or 0
        )

        # Recent tickets (last 7 days)
        recent_date = today - timedelta(days=7)
        recent_tickets = Booking.objects.filter(
            status="confirmed", created_at__date__gte=recent_date
        ).count()

        # Today's bookings count
        today_bookings = Booking.objects.filter(travel_date__date=today).count()

        return JsonResponse(
            {
                "active_tickets": active_tickets,
                "today_revenue": f"Le {today_revenue:,.0f}",
                "recent_tickets": recent_tickets,
                "today_bookings": today_bookings,
            }
        )
