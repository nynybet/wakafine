#!/usr/bin/env python
"""
Test script to verify booking creation page functionality
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine_bus.settings")
django.setup()

from django.test import Client, RequestFactory
from django.contrib.auth.models import User
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.http import HttpRequest
from bookings.views import BookingCreateView
from routes.models import Route
from buses.models import Bus
import json


def test_booking_context():
    """Test what context data is passed to the booking create view"""
    print("🧪 TESTING BOOKING CREATE CONTEXT")
    print("=" * 40)

    # Get test data
    route = Route.objects.first()
    bus = Bus.objects.filter(assigned_route=route).first()

    if not route or not bus:
        print("❌ No test data available (route or bus)")
        return

    print(f"Using Route: {route.id} - {route}")
    print(f"Using Bus: {bus.id} - {bus}")

    # Create a mock request
    factory = RequestFactory()
    request = factory.get(f"/bookings/create/?route={route.id}&bus={bus.id}")

    # Add required middleware attributes
    request.session = {}
    request.user = User.objects.filter(is_superuser=True).first()

    # Create view instance
    view = BookingCreateView()
    view.request = request

    # Get context data
    context = view.get_context_data()

    print(f"\n📊 CONTEXT DATA:")
    print(f"   Route in context: {'route' in context}")
    print(f"   Bus in context: {'bus' in context}")
    print(f"   Seats in context: {'seats' in context}")
    print(f"   Seats JSON in context: {'seats_json' in context}")

    if "route" in context:
        print(f"   Route object: {context['route']}")
        print(f"   Route price: {context['route'].price}")

    if "bus" in context:
        print(f"   Bus object: {context['bus']}")
        print(f"   Bus seat count: {context['bus'].seats.count()}")

    if "seats" in context:
        seats = context["seats"]
        print(f"   Seats data count: {len(seats)}")
        if seats:
            print(f"   First seat: {seats[0]}")
            available_count = sum(1 for seat in seats if seat.get("is_available"))
            print(f"   Available seats: {available_count}")

    if "seats_json" in context:
        try:
            seats_data = json.loads(context["seats_json"])
            print(f"   Seats JSON valid: True")
            print(f"   Seats JSON count: {len(seats_data)}")
        except json.JSONDecodeError:
            print(f"   Seats JSON valid: False")


def test_seat_rendering():
    """Test seat rendering functionality"""
    print("\n🪑 TESTING SEAT RENDERING")
    print("=" * 30)

    bus = Bus.objects.first()
    if not bus:
        print("❌ No bus available for testing")
        return

    seats = bus.seats.all()
    print(f"Bus: {bus}")
    print(f"Total seats in DB: {seats.count()}")

    for seat in seats[:5]:  # Show first 5 seats
        print(
            f"   Seat {seat.seat_number}: Window={seat.is_window}, Available={seat.is_available}"
        )


if __name__ == "__main__":
    test_booking_context()
    test_seat_rendering()
