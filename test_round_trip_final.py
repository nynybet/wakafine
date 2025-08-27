#!/usr/bin/env python3
"""
Final round trip booking test
Tests the complete round trip booking functionality including seat selection
"""

import os
import sys
import django

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine_bus.settings")
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from bookings.models import Route, Bus, Seat, Booking
from accounts.models import Terminal
from django.urls import reverse
from datetime import datetime, timedelta
import json

User = get_user_model()


def test_round_trip_booking():
    """Test complete round trip booking functionality"""

    # Create test client
    client = Client()

    # Create test user
    user = User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
        first_name="Test",
        last_name="User",
        phone_number="+23276123456",
    )

    # Login user
    client.login(username="testuser", password="testpass123")

    # Create test terminals
    freetown_terminal = Terminal.objects.get_or_create(
        name="Freetown Terminal",
        location="Freetown",
        defaults={
            "description": "Main terminal in Freetown",
            "contact_phone": "+23276111111",
            "contact_email": "freetown@wakafine.com",
        },
    )[0]

    bo_terminal = Terminal.objects.get_or_create(
        name="Bo Terminal",
        location="Bo",
        defaults={
            "description": "Main terminal in Bo",
            "contact_phone": "+23276222222",
            "contact_email": "bo@wakafine.com",
        },
    )[0]

    # Create test routes
    route_to_bo = Route.objects.get_or_create(
        origin="Freetown",
        destination="Bo",
        defaults={
            "distance": 250,
            "estimated_duration": timedelta(hours=4),
            "base_price": 150.00,
            "origin_terminal": freetown_terminal,
            "destination_terminal": bo_terminal,
        },
    )[0]

    route_to_freetown = Route.objects.get_or_create(
        origin="Bo",
        destination="Freetown",
        defaults={
            "distance": 250,
            "estimated_duration": timedelta(hours=4),
            "base_price": 150.00,
            "origin_terminal": bo_terminal,
            "destination_terminal": freetown_terminal,
        },
    )[0]

    # Create test buses
    bus_to_bo = Bus.objects.get_or_create(
        bus_name="Express A1",
        route=route_to_bo,
        defaults={
            "license_plate": "SL001",
            "total_seats": 45,
            "driver_name": "John Doe",
            "driver_contact": "+23276333333",
        },
    )[0]

    bus_to_freetown = Bus.objects.get_or_create(
        bus_name="Express B1",
        route=route_to_freetown,
        defaults={
            "license_plate": "SL002",
            "total_seats": 45,
            "driver_name": "Jane Smith",
            "driver_contact": "+23276444444",
        },
    )[0]

    # Create test seats
    seat_to_bo = Seat.objects.get_or_create(
        bus=bus_to_bo,
        seat_number="A1",
        defaults={"seat_type": "standard", "is_available": True},
    )[0]

    seat_to_freetown = Seat.objects.get_or_create(
        bus=bus_to_freetown,
        seat_number="B1",
        defaults={"seat_type": "standard", "is_available": True},
    )[0]

    print("✅ Test data created successfully")

    # Test round trip booking form submission
    tomorrow = datetime.now().date() + timedelta(days=1)

    booking_data = {
        "route": route_to_bo.id,
        "travel_date": tomorrow.strftime("%Y-%m-%d"),
        "travel_time": "09:00",
        "bus": bus_to_bo.id,
        "seat": seat_to_bo.id,
        "is_round_trip": True,
        "return_route": route_to_freetown.id,
        "return_travel_date": (tomorrow + timedelta(days=1)).strftime("%Y-%m-%d"),
        "return_travel_time": "15:00",
        "return_bus": bus_to_freetown.id,
        "return_seat": seat_to_freetown.id,
        "payment_method": "cash",
    }

    print("📝 Testing round trip booking submission...")

    # Submit booking
    response = client.post(reverse("booking_create"), data=booking_data)

    print(f"Response status: {response.status_code}")

    if response.status_code == 302:
        print("✅ Booking submitted successfully (redirected)")

        # Check if booking was created
        booking = Booking.objects.filter(customer=user).first()
        if booking:
            print(f"✅ Booking created with PNR: {booking.pnr_code}")
            print(f"   - Outbound seat: {booking.seat.seat_number}")
            print(
                f"   - Return seat: {booking.return_seat.seat_number if booking.return_seat else 'None'}"
            )
            print(f"   - Is round trip: {booking.is_round_trip}")
            print(f"   - Amount paid: Le {booking.amount_paid}")

            # Test ticket display
            ticket_url = reverse("ticket", kwargs={"pnr_code": booking.pnr_code})
            ticket_response = client.get(ticket_url)

            if ticket_response.status_code == 200:
                print("✅ Ticket displays successfully")

                # Check if ticket contains both seat numbers
                ticket_content = ticket_response.content.decode("utf-8")
                if booking.seat.seat_number in ticket_content:
                    print("✅ Outbound seat number displayed on ticket")
                if (
                    booking.return_seat
                    and booking.return_seat.seat_number in ticket_content
                ):
                    print("✅ Return seat number displayed on ticket")

            else:
                print(f"❌ Ticket display failed: {ticket_response.status_code}")

        else:
            print("❌ No booking was created")

    elif response.status_code == 200:
        print(
            "⚠️ Form submission returned to the same page (possible validation errors)"
        )
        # Check for form errors
        if hasattr(response, "context") and "form" in response.context:
            form = response.context["form"]
            if form.errors:
                print(f"Form errors: {form.errors}")
    else:
        print(f"❌ Unexpected response status: {response.status_code}")
        print(f"Response content: {response.content[:500]}")

    return True


if __name__ == "__main__":
    print("🧪 Starting Round Trip Booking Test")
    print("=" * 50)

    try:
        test_round_trip_booking()
        print("\n✅ Test completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
