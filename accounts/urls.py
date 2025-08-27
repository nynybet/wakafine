from django.urls import path
from . import views
from . import admin_views

app_name = "accounts"

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    # Admin URLs
    path(
        "admin/dashboard/",
        admin_views.AdminDashboardView.as_view(),
        name="admin_dashboard",
    ),
    path(
        "admin/users/", admin_views.ManageUsersView.as_view(), name="admin_manage_users"
    ),
    path(
        "admin/routes/",
        admin_views.ManageRoutesView.as_view(),
        name="admin_manage_routes",
    ),
    path(
        "admin/buses/", admin_views.ManageBusesView.as_view(), name="admin_manage_buses"
    ),
    path(
        "admin/bookings/",
        admin_views.ManageBookingsView.as_view(),
        name="admin_manage_bookings",
    ),
    path(
        "admin/tickets/",
        admin_views.ManageTicketsView.as_view(),
        name="admin_manage_tickets",
    ),
    path(
        "admin/terminals/",
        admin_views.ManageTerminalsView.as_view(),
        name="admin_manage_terminals",
    ),
    # Admin Actions
    path(
        "admin/users/<int:user_id>/toggle-status/",
        admin_views.ToggleUserStatusView.as_view(),
        name="admin_toggle_user_status",
    ),
    path(
        "admin/routes/<int:route_id>/toggle-status/",
        admin_views.ToggleRouteStatusView.as_view(),
        name="admin_toggle_route_status",
    ),
    path(
        "admin/buses/<int:bus_id>/toggle-status/",
        admin_views.ToggleBusStatusView.as_view(),
        name="admin_toggle_bus_status",
    ),
    path(
        "admin/terminals/<int:terminal_id>/toggle-status/",
        admin_views.ToggleTerminalStatusView.as_view(),
        name="admin_toggle_terminal_status",
    ),
    path(
        "admin/bookings/<int:booking_id>/update-status/",
        admin_views.UpdateBookingStatusView.as_view(),
        name="admin_update_booking_status",
    ),
    # Modal-based User Management URLs
    path(
        "admin/users/create/",
        admin_views.UserCreateModalView.as_view(),
        name="admin_user_create_modal",
    ),
    path(
        "admin/users/<int:user_id>/detail/",
        admin_views.UserDetailModalView.as_view(),
        name="admin_user_detail_modal",
    ),
    path(
        "admin/users/<int:user_id>/edit/",
        admin_views.UserEditModalView.as_view(),
        name="admin_user_edit_modal",
    ),
    path(
        "admin/users/<int:user_id>/delete-modal/",
        admin_views.UserDeleteModalView.as_view(),
        name="admin_user_delete_modal",
    ),
    # Delete URLs
    path(
        "admin/users/<int:pk>/delete/",
        admin_views.DeleteUserView.as_view(),
        name="admin_delete_user",
    ),
    path(
        "admin/routes/<int:pk>/delete/",
        admin_views.DeleteRouteView.as_view(),
        name="admin_delete_route",
    ),
    path(
        "admin/buses/<int:pk>/delete/",
        admin_views.DeleteBusView.as_view(),
        name="admin_delete_bus",
    ),
    path(
        "admin/bookings/<int:pk>/delete/",
        admin_views.DeleteBookingView.as_view(),
        name="admin_delete_booking",
    ),
    path(
        "admin/terminals/<int:pk>/delete/",
        admin_views.DeleteTerminalView.as_view(),
        name="admin_delete_terminal",
    ),
    # API endpoints
    path(
        "admin/api/ticket-stats/",
        admin_views.TicketQuickStatsAPIView.as_view(),
        name="admin_ticket_stats_api",
    ),
]
