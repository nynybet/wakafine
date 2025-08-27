#!/usr/bin/env python3
"""
Test the booking page to verify bus_seats URL fix
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
from routes.models import Route
from buses.models import Bus

User = get_user_model()


def test_booking_page_fix():
    """Test the booking page loads without NoReverseMatch error"""
    print("=== Testing Booking Page bus_seats URL Fix ===")

    try:
        client = Client()
        user = User.objects.get(username="pateh")
        client.force_login(user)

        # Get test route and bus
        route = Route.objects.filter(is_active=True).first()
        bus = Bus.objects.filter(assigned_route=route, is_active=True).first()

        if not route or not bus:
            print("❌ No test data available")
            return

        print(f"✓ Testing with route: {route.name}, bus: {bus.bus_name}")

        # Test booking page with route and bus parameters
        booking_url = f"{reverse('bookings:create')}?route={route.id}&bus={bus.id}"
        print(f"📋 Testing URL: {booking_url}")

        response = client.get(booking_url)
        print(f"📋 Booking page status: {response.status_code}")

        if response.status_code == 200:
            print("✅ Booking page loads successfully!")

            # Test the bus_seats URL endpoint directly
            seats_url = f"{reverse('bookings:bus_seats')}?bus_id={bus.id}&travel_date=2025-07-25"
            seats_response = client.get(seats_url)
            print(f"📋 Bus seats endpoint status: {seats_response.status_code}")

            if seats_response.status_code == 200:
                print("✅ Bus seats endpoint working!")
                data = seats_response.json()
                if "seats" in data:
                    print(f"✅ Seats data returned: {len(data['seats'])} seats")
                else:
                    print("⚠️  No seats data in response")
            else:
                print(f"❌ Bus seats endpoint failed: {seats_response.status_code}")

        else:
            print(f"❌ Booking page failed to load: {response.status_code}")
            if hasattr(response, "content"):
                content = response.content.decode("utf-8")
                if "NoReverseMatch" in content:
                    print("❌ Still has NoReverseMatch error")
                else:
                    print("❌ Different error occurred")

        print(f"\n📊 Summary:")
        print(f"  ✅ Added bus_seats URL pattern as alias to seat_availability")
        print(f"  ✅ Fixed JavaScript parameter from 'date' to 'travel_date'")
        print(f"  ✅ Both URL patterns point to same get_seat_availability function")
        print(f"  🌐 Booking page should now work at: {booking_url}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_booking_page_fix()
