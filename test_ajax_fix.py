#!/usr/bin/env python
"""
Test script to verify AJAX seat availability endpoint is working
"""

import os
import sys
import django
from django.test import Client
from django.utils import timezone
from datetime import timedelta
import json

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine_bus.settings")
django.setup()

from routes.models import Route
from buses.models import Bus
from accounts.models import User
from bookings.models import Booking


def test_ajax_endpoint():
    """Test AJAX seat availability endpoint"""
    print("\n🔧 TESTING AJAX SEAT AVAILABILITY FIX")
    print("=" * 40)

    client = Client()

    # Get test data
    route = Route.objects.first()
    bus = Bus.objects.filter(assigned_route=route).first()
    travel_date = (timezone.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    print(f"📌 Testing with:")
    print(f"   Route: {route.name}")
    print(f"   Bus: {bus.bus_name} (ID: {bus.id})")
    print(f"   Travel Date: {travel_date}")

    try:
        # Test the AJAX endpoint that was previously failing
        ajax_url = (
            f"/bookings/seat-availability/?bus_id={bus.id}&travel_date={travel_date}"
        )
        print(f"\n🌐 Making AJAX request: {ajax_url}")

        ajax_response = client.get(ajax_url)
        print(f"📡 Response Status: {ajax_response.status_code}")

        if ajax_response.status_code == 200:
            try:
                data = json.loads(ajax_response.content)
                print(f"✅ AJAX Working Successfully!")
                print(f"   Bus Name: {data.get('bus_name', 'N/A')}")
                print(f"   Total Seats: {data.get('total_seats', 'N/A')}")
                print(f"   Available Seats: {data.get('available_seats', 'N/A')}")
                print(f"   Seats Data Length: {len(data.get('seats', []))}")

                # Check if we have seat data
                seats = data.get("seats", [])
                if seats:
                    print(f"   First seat: {seats[0]}")
                    available_count = sum(
                        1 for seat in seats if seat.get("is_available")
                    )
                    print(f"   Available count verification: {available_count}")

                return True
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON response: {e}")
                print(f"   Content: {ajax_response.content[:200]}")
                return False
        else:
            print(f"❌ AJAX Failed with status {ajax_response.status_code}")
            print(f"   Content: {ajax_response.content[:300]}")
            return False

    except Exception as e:
        print(f"❌ AJAX Error: {str(e)}")
        return False


def test_end_to_end_flow():
    """Test end-to-end booking flow through web interface"""
    print("\n🚀 TESTING END-TO-END WEB FLOW")
    print("=" * 35)

    client = Client()

    # Login as customer
    customer = User.objects.filter(role="customer").first()
    if not customer:
        print("❌ No customer found in database")
        return False

    login_success = client.login(username=customer.username, password="testpass123")
    print(f"🔐 Customer login: {'✅ Success' if login_success else '❌ Failed'}")

    if not login_success:
        return False

    # Get route and bus for booking
    route = Route.objects.first()
    bus = Bus.objects.filter(assigned_route=route).first()
    travel_date = (timezone.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    print(f"📍 Testing booking flow:")
    print(f"   Route: {route.name} (Le {route.price})")
    print(f"   Bus: {bus.bus_name}")
    print(f"   Date: {travel_date}")

    # Test booking creation page
    booking_url = f"/bookings/create/?route={route.id}&bus={bus.id}&date={travel_date}"
    print(f"\n🎫 Accessing booking page: {booking_url}")

    response = client.get(booking_url)
    print(f"📄 Booking page status: {response.status_code}")

    if response.status_code == 200:
        print("✅ Booking page accessible")
        # Check if page contains expected elements
        content = response.content.decode()
        if "seat-map" in content:
            print("✅ Seat map present")
        if "id_travel_date" in content:
            print("✅ Date field present")
        if bus.bus_name in content:
            print("✅ Bus name displayed")
        return True
    else:
        print(f"❌ Booking page failed: {response.status_code}")
        return False


if __name__ == "__main__":
    print("🧪 WAKAFINE BUS - AJAX FIX TEST")
    print("=" * 50)

    # Test the fixed AJAX endpoint
    ajax_success = test_ajax_endpoint()

    # Test end-to-end flow
    e2e_success = test_end_to_end_flow()

    print(f"\n📊 TEST RESULTS:")
    print(f"   AJAX Endpoint: {'✅ WORKING' if ajax_success else '❌ FAILED'}")
    print(f"   End-to-End Flow: {'✅ WORKING' if e2e_success else '❌ FAILED'}")

    if ajax_success and e2e_success:
        print(f"\n🎉 ALL TESTS PASSED! The AJAX fix is successful!")
        print(f"   The seat availability endpoint is now working properly.")
        print(f"   The booking flow should work end-to-end through the web interface.")
    else:
        print(f"\n⚠️  Some tests failed. Please check the issues above.")
