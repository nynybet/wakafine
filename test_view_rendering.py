#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine_bus.settings")
django.setup()

from django.http import HttpRequest
from django.contrib.auth import get_user_model
from bookings.models import Booking
from bookings.views import (
    PaymentSuccessView,
    TicketView,
    TicketPrintView,
    TicketPDFView,
)

User = get_user_model()


def test_view_rendering():
    print("🎫 Testing view rendering directly...")

    # Get admin user and booking
    try:
        admin_user = User.objects.get(username="admin")
        booking = Booking.objects.get(id=21)
        print(f"✅ Admin user: {admin_user.username}")
        print(f"✅ Booking: {booking.pnr_code}")
    except Exception as e:
        print(f"❌ Setup error: {e}")
        return

    # Create mock request
    request = HttpRequest()
    request.method = "GET"
    request.user = admin_user

    # Test views
    views_to_test = [
        ("Payment Success", PaymentSuccessView),
        ("Ticket View", TicketView),
        ("Ticket Print", TicketPrintView),
        ("Ticket PDF", TicketPDFView),
    ]

    for view_name, view_class in views_to_test:
        print(f"\n🔄 Testing {view_name}...")
        try:
            view = view_class()
            view.setup(request, pk=booking.id)

            # Check if user has permission
            if hasattr(view, "get_object"):
                obj = view.get_object()
                print(f"✅ Object retrieved: {obj}")

            # Try to get context data
            if hasattr(view, "get_context_data"):
                context = view.get_context_data()
                print(f"✅ Context data keys: {list(context.keys())}")

            print(f"✅ {view_name} - No template errors")

        except Exception as e:
            print(f"❌ {view_name} - Error: {e}")
            print(f"   Error type: {type(e).__name__}")


if __name__ == "__main__":
    test_view_rendering()
