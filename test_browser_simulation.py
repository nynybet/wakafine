#!/usr/bin/env python3
"""
Final verification test for seat selection fix - simulating browser behavior
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
from bookings.forms import BookingForm
from routes.models import Route
from buses.models import Bus, Seat
import json

User = get_user_model()


def test_ajax_seat_loading():
    """Test AJAX seat loading functionality"""
    print("=== Testing AJAX Seat Loading ===")

    try:
        client = Client()
        user = User.objects.get(username="pateh")
        client.force_login(user)

        # Get test data
        route = Route.objects.filter(is_active=True).first()
        bus = Bus.objects.filter(assigned_route=route, is_active=True).first()

        if not all([route, bus]):
            print("❌ Missing test data")
            return

        print(f"✓ Testing with:")
        print(f"  Route: {route}")
        print(f"  Bus: {bus}")

        # Test AJAX seat availability endpoint
        response = client.get(
            reverse("bookings:seat_availability"),
            {"bus_id": bus.id, "travel_date": "2025-07-16"},
        )

        print(f"📋 AJAX Response status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ AJAX response received:")
            print(f"  Seats returned: {len(data.get('seats', []))}")
            print(f"  Available seats: {data.get('available_seats', 0)}")
            print(f"  Total seats: {data.get('total_seats', 0)}")

            # Test specific seat data
            seats = data.get("seats", [])
            if seats:
                first_seat = seats[0]
                print(
                    f"  First seat example: ID {first_seat['id']}, Number {first_seat['number']}, Available: {first_seat['is_available']}"
                )
        else:
            print("❌ AJAX request failed")

    except Exception as e:
        print(f"❌ AJAX test failed: {e}")


def test_form_with_different_scenarios():
    """Test form validation with different seat selection scenarios"""
    print("\n=== Testing Form Validation Scenarios ===")

    try:
        route = Route.objects.filter(is_active=True).first()
        bus = Bus.objects.filter(assigned_route=route, is_active=True).first()
        seats = Seat.objects.filter(bus=bus, is_available=True)[:3]  # Get 3 seats

        if not all([route, bus]) or len(seats) < 2:
            print("❌ Insufficient test data")
            return

        # Scenario 1: Valid seat selection
        print("🧪 Scenario 1: Valid seat selection")
        form_data = {
            "route": route.id,
            "bus": bus.id,
            "seat": seats[0].id,
            "trip_type": "one_way",
            "travel_date": "2025-07-16",
        }

        form = BookingForm(data=form_data)
        print(f"  Form valid: {form.is_valid()}")
        if not form.is_valid():
            print(f"  Errors: {form.errors}")

        # Scenario 2: Invalid seat for different bus
        print("\n🧪 Scenario 2: Seat from different bus")
        other_bus = Bus.objects.exclude(id=bus.id).first()
        if other_bus:
            other_seat = Seat.objects.filter(bus=other_bus, is_available=True).first()
            if other_seat:
                form_data_invalid = form_data.copy()
                form_data_invalid["seat"] = other_seat.id

                form_invalid = BookingForm(data=form_data_invalid)
                print(f"  Form valid: {form_invalid.is_valid()}")
                if not form_invalid.is_valid():
                    print(f"  Expected error found: {form_invalid.errors}")

        # Scenario 3: Round trip validation
        print("\n🧪 Scenario 3: Round trip validation")
        form_data_rt = form_data.copy()
        form_data_rt["trip_type"] = "round_trip"
        form_data_rt["return_date"] = "2025-07-20"

        form_rt = BookingForm(data=form_data_rt)
        print(f"  Round trip form valid: {form_rt.is_valid()}")
        if not form_rt.is_valid():
            print(f"  Errors: {form_rt.errors}")

    except Exception as e:
        print(f"❌ Form validation test failed: {e}")


def test_browser_simulation():
    """Simulate browser-like form submission"""
    print("\n=== Browser Simulation Test ===")

    try:
        client = Client()
        user = User.objects.get(username="pateh")
        client.force_login(user)

        # Step 1: Get booking form page
        print("📄 Step 1: Loading booking form...")
        response = client.get(reverse("bookings:create"))
        print(f"  Form page status: {response.status_code}")

        # Step 2: Get route buses via AJAX (simulate JS)
        route = Route.objects.filter(is_active=True).first()
        print(f"\n🔄 Step 2: Loading buses for route {route}...")
        response = client.get(reverse("bookings:route_buses"), {"route_id": route.id})
        print(f"  Route buses response: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            buses = data.get("buses", [])
            print(f"  Buses available: {len(buses)}")

        # Step 3: Get seat availability
        if buses:
            bus_id = buses[0]["id"]
            print(f"\n💺 Step 3: Loading seats for bus {bus_id}...")
            response = client.get(
                reverse("bookings:seat_availability"),
                {"bus_id": bus_id, "travel_date": "2025-07-16"},
            )
            print(f"  Seat availability response: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                seats = data.get("seats", [])
                available_seats = [s for s in seats if s["is_available"]]
                print(f"  Available seats: {len(available_seats)}")

                # Step 4: Submit booking with selected seat
                if available_seats:
                    seat_id = available_seats[0]["id"]
                    print(f"\n🚀 Step 4: Submitting booking with seat {seat_id}...")

                    booking_data = {
                        "route": route.id,
                        "bus": bus_id,
                        "seat": seat_id,
                        "trip_type": "one_way",
                        "travel_date": "2025-07-16",
                    }

                    response = client.post(
                        reverse("bookings:create"), data=booking_data
                    )
                    print(f"  Booking submission response: {response.status_code}")

                    if response.status_code == 302:
                        print("✅ Complete browser simulation successful!")
                    else:
                        print("❌ Booking submission failed")

    except Exception as e:
        print(f"❌ Browser simulation failed: {e}")


if __name__ == "__main__":
    test_ajax_seat_loading()
    test_form_with_different_scenarios()
    test_browser_simulation()
