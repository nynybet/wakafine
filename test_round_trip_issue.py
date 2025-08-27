#!/usr/bin/env python3
"""
Test round trip booking submission issue
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine_bus.settings")
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from bookings.models import Booking
from routes.models import Route
from buses.models import Bus, Seat

User = get_user_model()


def test_round_trip_submission():
    """Test round trip booking submission"""
    print("=== Testing Round Trip Submission Issue ===")

    try:
        client = Client()
        user = User.objects.get(username="pateh")
        client.force_login(user)

        # Get test data
        route = Route.objects.filter(is_active=True).first()
        bus = Bus.objects.filter(assigned_route=route, is_active=True).first()
        seat = Seat.objects.filter(bus=bus, is_available=True).first()

        if not all([route, bus, seat]):
            print("❌ Missing test data")
            return

        print(f"✓ Using test data:")
        print(f"  Route: {route}")
        print(f"  Bus: {bus}")
        print(f"  Seat: {seat}")

        # Test round trip form submission
        booking_data = {
            "route": route.id,
            "bus": bus.id,
            "seat": seat.id,
            "trip_type": "round_trip",
            "travel_date": "2025-07-20",
            "return_date": "2025-07-22",
        }

        print(f"\n🧪 Testing round trip submission...")
        print(f"Form data: {booking_data}")

        # First check the create form
        response = client.get(reverse("bookings:create"))
        print(f"📋 Create form status: {response.status_code}")

        # Submit round trip booking
        response = client.post(reverse("bookings:create"), data=booking_data)
        print(f"📋 Round trip submission status: {response.status_code}")

        if response.status_code == 302:  # Redirect expected on success
            print("✅ Round trip submission successful!")

            # Check if booking was created
            booking = (
                Booking.objects.filter(customer=user).order_by("-booking_date").first()
            )
            if booking and booking.trip_type == "round_trip":
                print(f"✅ Round trip booking created:")
                print(f"  PNR: {booking.pnr_code}")
                print(f"  Trip Type: {booking.trip_type}")
                print(f"  Travel Date: {booking.travel_date}")
                print(f"  Return Date: {booking.return_date}")
                print(f"  Amount: Le {booking.amount_paid}")
            else:
                print("❌ Booking not found or not round trip")

        else:
            print(f"❌ Round trip submission failed with status {response.status_code}")
            if hasattr(response, "content"):
                content = response.content.decode("utf-8")
                if "error" in content.lower():
                    print("Response contains errors")

        # Test one-way for comparison
        booking_data_oneway = booking_data.copy()
        booking_data_oneway["trip_type"] = "one_way"
        booking_data_oneway.pop("return_date", None)

        print(f"\n🧪 Testing one-way submission for comparison...")
        response = client.post(reverse("bookings:create"), data=booking_data_oneway)
        print(f"📋 One-way submission status: {response.status_code}")

        if response.status_code == 302:
            print("✅ One-way submission works")
        else:
            print("❌ One-way submission also failed")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_round_trip_submission()
