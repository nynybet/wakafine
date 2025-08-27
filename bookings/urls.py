from django.urls import path
from . import views

app_name = "bookings"

urlpatterns = [
    path("", views.BookingListView.as_view(), name="list"),
    path("create/", views.BookingCreateView.as_view(), name="create"),
    path("<int:pk>/", views.BookingDetailView.as_view(), name="detail"),
    path("<int:pk>/ticket/", views.TicketView.as_view(), name="ticket"),
    path("<int:pk>/ticket/print/", views.TicketView.as_view(), name="ticket_print"),
    path("search/", views.BookingSearchView.as_view(), name="search"),
    path("payment/<int:pk>/", views.PaymentView.as_view(), name="payment"),
    path(
        "payment/success/<int:pk>/",
        views.PaymentSuccessView.as_view(),
        name="payment_success",
    ),
    path("<int:pk>/ticket/pdf/", views.TicketPDFView.as_view(), name="ticket_pdf"),
    path("seat-availability/", views.get_seat_availability, name="seat_availability"),
    path(
        "bus-seats/", views.get_seat_availability, name="bus_seats"
    ),  # Alias for return seats
    path("route-buses/", views.get_route_buses_ajax, name="route_buses"),
    path("debug/", views.BookingDebugView.as_view(), name="debug"),
]
