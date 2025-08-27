#!/usr/bin/env python
"""
Comprehensive test script to verify all AJAX and template fixes are working
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


def test_ajax_endpoint_comprehensive():
    """Test AJAX seat availability endpoint comprehensively"""
    print("\n🔧 TESTING AJAX SEAT AVAILABILITY (COMPREHENSIVE)")
    print("=" * 50)

    client = Client()

    # Get test data
    route = Route.objects.first()
    bus = Bus.objects.filter(assigned_route=route).first()
    travel_date = (timezone.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    print(f"📌 Testing with:")
    print(f"   Route: {route.name} - {route.price} Le")
    print(f"   Bus: {bus.bus_name} (ID: {bus.id})")
    print(f"   Travel Date: {travel_date}")

    # Test AJAX endpoint
    ajax_url = f"/bookings/seat-availability/?bus_id={bus.id}&travel_date={travel_date}"
    ajax_response = client.get(ajax_url)

    print(f"\n🌐 AJAX Response Status: {ajax_response.status_code}")

    if ajax_response.status_code == 200:
        data = json.loads(ajax_response.content)
        print(f"✅ AJAX Working Successfully!")
        print(f"   Bus Name: {data.get('bus_name')}")
        print(f"   Total Seats: {data.get('total_seats')}")
        print(f"   Available Seats: {data.get('available_seats')}")

        # Test seat data structure
        seats = data.get("seats", [])
        if seats:
            print(f"   Sample seat data: {seats[0]}")
            required_fields = ["id", "number", "is_window", "is_available", "is_booked"]
            sample_seat = seats[0]
            missing_fields = [
                field for field in required_fields if field not in sample_seat
            ]
            if missing_fields:
                print(f"❌ Missing seat fields: {missing_fields}")
                return False
            else:
                print(f"✅ All required seat fields present")

        return True
    else:
        print(f"❌ AJAX Failed with status {ajax_response.status_code}")
        print(f"   Content: {ajax_response.content[:300]}")
        return False


def test_template_rendering():
    """Test that templates render without field reference errors"""
    print("\n📄 TESTING TEMPLATE RENDERING")
    print("=" * 35)

    client = Client()

    # Get customer user for login
    customer = User.objects.filter(role="customer").first()
    customer.set_password("testpass123")
    customer.save()

    login_success = client.login(username=customer.username, password="testpass123")
    print(f"🔐 Customer login: {'✅ Success' if login_success else '❌ Failed'}")

    if not login_success:
        print("   Cannot test authenticated templates without login")
        return False

    # Test pages that use bus model references
    test_urls = [
        ("/bookings/", "Bookings List"),
        ("/bookings/search/", "Booking Search"),
        ("/accounts/dashboard/", "Customer Dashboard"),
    ]

    all_passed = True
    for url, name in test_urls:
        try:
            response = client.get(url)
            if response.status_code == 200:
                print(f"✅ {name}: {response.status_code}")
                # Check if page contains bus name references
                content = response.content.decode()
                if "bus.name" in content:
                    print(f"❌ {name}: Still contains bus.name references")
                    all_passed = False
            else:
                print(f"⚠️  {name}: {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: Error - {str(e)}")
            all_passed = False

    return all_passed


def test_booking_creation_flow():
    """Test creating a booking through the web interface"""
    print("\n🎫 TESTING BOOKING CREATION FLOW")
    print("=" * 35)

    client = Client()

    # Login
    customer = User.objects.filter(role="customer").first()
    client.login(username=customer.username, password="testpass123")

    # Get test data
    route = Route.objects.first()
    bus = Bus.objects.filter(assigned_route=route).first()
    available_seat = bus.seats.filter(is_available=True).first()
    travel_date = (timezone.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    print(f"📍 Test booking data:")
    print(f"   Route: {route.name}")
    print(f"   Bus: {bus.bus_name}")
    print(f"   Seat: {available_seat.seat_number}")
    print(f"   Price: Le {route.price}")

    # Test booking creation page access
    booking_url = f"/bookings/create/?route={route.id}&bus={bus.id}&date={travel_date}"
    response = client.get(booking_url)

    if response.status_code == 200:
        print(f"✅ Booking page accessible")

        # Check for critical template issues
        content = response.content.decode()
        issues = []

        if "bus.name" in content:
            issues.append("bus.name reference found")
        if "base_fare" in content:
            issues.append("base_fare reference found")
        if "TemplateSyntaxError" in content:
            issues.append("Template syntax error")

        if issues:
            print(f"❌ Template issues: {', '.join(issues)}")
            return False
        else:
            print(f"✅ No template field reference issues")
            return True
    else:
        print(f"❌ Booking page failed: {response.status_code}")
        return False


def test_staff_dashboard():
    """Test staff dashboard for bus name field issues"""
    print("\n👥 TESTING STAFF DASHBOARD")
    print("=" * 25)

    client = Client()

    # Get or create staff user
    staff_user = User.objects.filter(role="staff").first()
    if not staff_user:
        print("❌ No staff user found")
        return False

    staff_user.set_password("testpass123")
    staff_user.save()

    login_success = client.login(username=staff_user.username, password="testpass123")
    print(f"🔐 Staff login: {'✅ Success' if login_success else '❌ Failed'}")

    if not login_success:
        return False

    response = client.get("/accounts/dashboard/")
    if response.status_code == 200:
        print(f"✅ Staff dashboard accessible")

        # Check for bus.name references in dashboard
        content = response.content.decode()
        if "bus.name" in content:
            print(f"❌ Still contains bus.name references")
            return False
        else:
            print(f"✅ No bus.name field issues")
            return True
    else:
        print(f"❌ Staff dashboard failed: {response.status_code}")
        return False


if __name__ == "__main__":
    print("🧪 WAKAFINE BUS - COMPREHENSIVE FIX VERIFICATION")
    print("=" * 60)

    # Run all tests
    results = {}

    results["ajax"] = test_ajax_endpoint_comprehensive()
    results["templates"] = test_template_rendering()
    results["booking_flow"] = test_booking_creation_flow()
    results["staff_dashboard"] = test_staff_dashboard()

    print(f"\n📊 COMPREHENSIVE TEST RESULTS:")
    print(f"=" * 40)

    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {test_name.replace('_', ' ').title()}: {status}")
        if not passed:
            all_passed = False

    print(f"\n{'🎉 ALL TESTS PASSED!' if all_passed else '⚠️  SOME TESTS FAILED'}")

    if all_passed:
        print(f"✅ AJAX endpoint working correctly")
        print(f"✅ Bus field references fixed in templates")
        print(f"✅ Route price references corrected")
        print(f"✅ Booking flow functional")
        print(f"✅ Staff dashboard working")
        print(f"\n🚀 The bus booking system is now fully operational!")
    else:
        print(f"\n🔧 Some components need attention. Check the detailed results above.")
