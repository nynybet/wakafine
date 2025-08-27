#!/usr/bin/env python3
"""
Comprehensive test to verify booking flow with seat selection works
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


def test_complete_booking_flow():
    """Test the complete booking flow from seat selection to booking creation"""
    print("=== Testing Complete Booking Flow ===")

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

        # Test booking creation via POST
        booking_data = {
            "route": route.id,
            "bus": bus.id,
            "seat": seat.id,
            "trip_type": "one_way",
            "travel_date": "2025-07-16",
        }

        print(f"\n🚀 Testing booking creation via POST request...")
        response = client.post(reverse("bookings:create"), data=booking_data)

        print(f"📋 Response status: {response.status_code}")

        if response.status_code == 302:  # Successful redirect
            print("✅ Booking created successfully!")

            # Get the created booking
            booking = (
                Booking.objects.filter(customer=user).order_by("-created_at").first()
            )
            if booking:
                print(f"  📄 Booking details:")
                print(f"    PNR: {booking.pnr_code}")
                print(f"    Route: {booking.route}")
                print(f"    Bus: {booking.bus}")
                print(f"    Seat: {booking.seat}")
                print(f"    Amount: Le {booking.amount_paid}")
                print(f"    Trip Type: {booking.trip_type}")

                # Test payment page access
                payment_url = reverse("bookings:payment", kwargs={"pk": booking.pk})
                payment_response = client.get(payment_url)
                print(
                    f"  💳 Payment page access: {payment_response.status_code} (should be 200)"
                )

                if payment_response.status_code == 200:
                    print("✅ Payment page accessible!")
                else:
                    print("❌ Payment page not accessible")

            else:
                print("❌ No booking found after creation")

        elif response.status_code == 200:  # Form has errors
            print("❌ Form validation failed")
            # Try to get form errors from context
            if hasattr(response, "context") and "form" in response.context:
                form = response.context["form"]
                if form.errors:
                    print("  Form errors:")
                    for field, errors in form.errors.items():
                        print(f"    {field}: {errors}")
        else:
            print(f"❌ Unexpected response status: {response.status_code}")

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()


def test_round_trip_booking():
    """Test round trip booking functionality"""
    print("\n=== Testing Round Trip Booking ===")

    try:
        client = Client()
        user = User.objects.get(username="pateh")
        client.force_login(user)

        # Get test data
        route = Route.objects.filter(is_active=True).first()
        bus = Bus.objects.filter(assigned_route=route, is_active=True).first()
        seat = (
            Seat.objects.filter(bus=bus, is_available=True)
            .exclude(booking__status__in=["confirmed", "pending"])
            .first()
        )

        if not all([route, bus, seat]):
            print("❌ Missing test data for round trip")
            return

        # Test round trip booking
        booking_data = {
            "route": route.id,
            "bus": bus.id,
            "seat": seat.id,
            "trip_type": "round_trip",
            "travel_date": "2025-07-17",
            "return_date": "2025-07-20",
        }

        print(f"✓ Testing round trip booking...")
        print(f"  Base price: Le {route.price}")
        print(f"  Expected total: Le {route.price * 2}")

        response = client.post(reverse("bookings:create"), data=booking_data)

        if response.status_code == 302:  # Successful redirect
            print("✅ Round trip booking created!")

            booking = (
                Booking.objects.filter(customer=user).order_by("-created_at").first()
            )
            if booking and booking.trip_type == "round_trip":
                print(f"  📄 Round trip details:")
                print(f"    Trip type: {booking.trip_type}")
                print(f"    Travel date: {booking.travel_date.date()}")
                print(f"    Return date: {booking.return_date.date()}")
                print(f"    Amount paid: Le {booking.amount_paid}")
                print(
                    f"    Price calculation correct: {booking.amount_paid == route.price * 2}"
                )

        else:
            print("❌ Round trip booking failed")

    except Exception as e:
        print(f"❌ Round trip test failed: {e}")


if __name__ == "__main__":
    test_complete_booking_flow()
    test_round_trip_booking()
