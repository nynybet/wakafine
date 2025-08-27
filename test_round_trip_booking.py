#!/usr/bin/env python3
"""
Test script for round trip booking functionality
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine_bus.settings")
django.setup()

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from bookings.models import Booking
from routes.models import Route
from buses.models import Bus, Seat
from accounts.models import Terminal
from datetime import datetime, timedelta
from django.urls import reverse

User = get_user_model()


def test_round_trip_booking_form():
    """Test round trip booking form submission"""

    print("🧪 Testing Round Trip Booking Form Submission")
    print("=" * 50)

    # Create test client
    client = Client()

    # Create test user
    user, created = User.objects.get_or_create(
        username="roundtrip_test_user",
        defaults={
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "phone_number": "+23276123456",
        },
    )

    if created:
        user.set_password("testpass123")
        user.save()
        print(f"✅ Created test user: {user.username}")
    else:
        print(f"✅ Using existing test user: {user.username}")

    # Login user
    login_success = client.login(username="roundtrip_test_user", password="testpass123")
    print(f"✅ User login: {'Success' if login_success else 'Failed'}")

    # Get test data
    routes = Route.objects.all()[:2]
    if len(routes) < 2:
        print("❌ Need at least 2 routes for testing")
        return False

    route = routes[0]
    buses = Bus.objects.filter(assigned_route=route)[:2]

    if len(buses) < 2:
        print("❌ Need at least 2 buses for testing")
        return False

    bus1, bus2 = buses[0], buses[1]

    # Get available seats
    seats1 = Seat.objects.filter(bus=bus1, is_available=True)[:1]
    seats2 = Seat.objects.filter(bus=bus2, is_available=True)[:1]

    if not seats1 or not seats2:
        print("❌ Need available seats on both buses")
        return False

    seat1, seat2 = seats1[0], seats2[0]

    print(f"✅ Test data ready:")
    print(f"   Route: {route}")
    print(f"   Bus 1: {bus1} (Seat: {seat1.seat_number})")
    print(f"   Bus 2: {bus2} (Seat: {seat2.seat_number})")

    # Test form submission
    tomorrow = (datetime.now().date() + timedelta(days=1)).strftime("%Y-%m-%d")
    day_after = (datetime.now().date() + timedelta(days=2)).strftime("%Y-%m-%d")

    form_data = {
        "route": route.id,
        "bus": bus1.id,
        "seat": seat1.id,
        "trip_type": "round_trip",
        "travel_date": tomorrow,
        "return_date": day_after,
        "return_bus": bus2.id,
        "return_seat": seat2.id,
        "payment_method": "cash",
    }

    print(f"\n📝 Submitting round trip booking form...")
    print(f"   Form data: {form_data}")

    response = client.post(reverse("bookings:create"), data=form_data)

    print(f"   Response status: {response.status_code}")

    if response.status_code == 302:
        print("✅ Form submission successful (redirected)")

        # Check if booking was created
        booking = Booking.objects.filter(customer=user).order_by("-created_at").first()

        if booking:
            print(f"✅ Booking created successfully!")
            print(f"   PNR: {booking.pnr_code}")
            print(f"   Trip Type: {booking.trip_type}")
            print(f"   Is Round Trip: {booking.is_round_trip}")
            print(f"   Outbound Seat: {booking.seat.seat_number}")
            print(
                f"   Return Seat: {booking.return_seat.seat_number if booking.return_seat else 'None'}"
            )
            print(
                f"   Return Bus: {booking.return_bus if booking.return_bus else 'None'}"
            )
            print(f"   Amount: Le {booking.amount_paid}")

            return True
        else:
            print("❌ No booking was created")
            return False

    elif response.status_code == 200:
        print("⚠️ Form returned to same page (validation errors)")
        content = response.content.decode("utf-8")
        if "error" in content.lower():
            print("   Found errors in response")
        return False
    else:
        print(f"❌ Unexpected response: {response.status_code}")
        return False


if __name__ == "__main__":
    try:
        success = test_round_trip_booking_form()
        if success:
            print("\n🎉 Round trip booking test PASSED!")
        else:
            print("\n❌ Round trip booking test FAILED!")
    except Exception as e:
        print(f"\n💥 Test failed with exception: {e}")
        import traceback

        traceback.print_exc()
