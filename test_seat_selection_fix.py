#!/usr/bin/env python3
"""
Test script to verify the seat selection fix
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
from bookings.forms import BookingForm

User = get_user_model()


def test_seat_selection_form():
    """Test that seat selection form validation works correctly"""
    print("=== Testing Seat Selection Form Fix ===")

    try:
        # Get test data
        user = User.objects.get(username="pateh")
        route = Route.objects.filter(is_active=True).first()
        bus = Bus.objects.filter(assigned_route=route, is_active=True).first()
        seat = Seat.objects.filter(bus=bus, is_available=True).first()

        if not all([route, bus, seat]):
            print("❌ Missing test data: route, bus, or seat not found")
            return

        print(f"✓ Test data found:")
        print(
            f"  Route: {route.get_origin_display()} to {route.get_destination_display()}"
        )
        print(f"  Bus: {bus.bus_name} ({bus.bus_number})")
        print(f"  Seat: {seat.seat_number}")

        # Test form with valid data
        form_data = {
            "route": route.id,
            "bus": bus.id,
            "seat": seat.id,
            "trip_type": "one_way",
            "travel_date": "2025-07-15",  # Future date
        }

        print(f"\n🧪 Testing form validation with data:")
        for key, value in form_data.items():
            print(f"  {key}: {value}")

        # Create form instance
        form = BookingForm(data=form_data)

        print(f"\n📋 Form validation results:")
        print(f"  Form is valid: {form.is_valid()}")

        if not form.is_valid():
            print("❌ Form errors found:")
            for field, errors in form.errors.items():
                print(f"  {field}: {errors}")
        else:
            print("✅ Form validation passed!")

            # Test actual booking creation
            print(f"\n🚀 Testing booking creation...")
            booking_data = form.cleaned_data.copy()
            booking_data["customer"] = user
            booking_data["amount_paid"] = route.price

            try:
                # Don't actually save, just test creation
                booking = Booking(**booking_data)
                print("✅ Booking object creation successful!")
                print(f"  Route: {booking.route}")
                print(f"  Bus: {booking.bus}")
                print(f"  Seat: {booking.seat}")
                print(f"  Customer: {booking.customer}")

            except Exception as e:
                print(f"❌ Booking creation failed: {e}")

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()


def test_seat_queryset_update():
    """Test that seat queryset is properly updated"""
    print("\n=== Testing Seat Queryset Update ===")

    try:
        route = Route.objects.filter(is_active=True).first()
        bus = Bus.objects.filter(assigned_route=route, is_active=True).first()

        if not all([route, bus]):
            print("❌ Missing test data: route or bus not found")
            return

        print(f"✓ Testing with bus: {bus.bus_name}")
        print(f"  Available seats: {bus.seats.filter(is_available=True).count()}")

        # Test form initialization with POST data
        form_data = {
            "route": route.id,
            "bus": bus.id,
        }

        form = BookingForm(data=form_data)

        print(f"📋 Seat queryset after initialization:")
        print(f"  Seat queryset count: {form.fields['seat'].queryset.count()}")
        print(f"  Expected count: {bus.seats.filter(is_available=True).count()}")

        if form.fields["seat"].queryset.count() > 0:
            print("✅ Seat queryset properly populated!")
            first_seat = form.fields["seat"].queryset.first()
            print(f"  First available seat: {first_seat.seat_number}")
        else:
            print("❌ Seat queryset is empty")

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_seat_selection_form()
    test_seat_queryset_update()
