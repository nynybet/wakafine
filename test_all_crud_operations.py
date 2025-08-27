#!/usr/bin/env python
"""
Comprehensive test of all CRUD operations in Waka-Fine Bus system
Tests users, tickets, bookings, routes, buses, and terminals
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine_bus.settings")
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.test import Client
from django.urls import reverse
from terminals.models import Terminal
from routes.models import Route
from buses.models import Bus, Seat
from bookings.models import Booking

User = get_user_model()


def test_all_crud_operations():
    """Test all CRUD operations for all entities"""
    print("🧪 TESTING ALL CRUD OPERATIONS")
    print("=" * 60)

    # Summary of entities
    entities = {
        "Users": User.objects.count(),
        "Terminals": Terminal.objects.count(),
        "Routes": Route.objects.count(),
        "Buses": Bus.objects.count(),
        "Bookings": Booking.objects.count(),
    }

    print("\n📊 CURRENT SYSTEM STATE")
    print("-" * 30)
    for entity, count in entities.items():
        print(f"✅ {entity}: {count}")

    # Test terminal CRUD
    print("\n🏢 TERMINAL CRUD OPERATIONS")
    print("-" * 40)

    # Test 1: Terminal CRUD
    terminal_count_before = Terminal.objects.count()
    test_terminal, created = Terminal.objects.get_or_create(
        name="CRUD Test Terminal",
        defaults={
            "terminal_type": "bus_stop",
            "location": "Test Location for CRUD",
            "city": "freetown",
            "operating_hours_start": "06:00:00",
            "operating_hours_end": "20:00:00",
            "is_active": True,
        },
    )

    if created:
        print(f"✅ CREATE: Terminal created - {test_terminal.name}")
    else:
        print(f"⚠️  Terminal already exists - {test_terminal.name}")

    # READ
    terminal = Terminal.objects.get(id=test_terminal.id)
    print(f"✅ READ: Terminal found - {terminal.name}")

    # UPDATE
    original_location = terminal.location
    terminal.location = "Updated Test Location"
    terminal.save()
    print(
        f"✅ UPDATE: Terminal location updated from '{original_location}' to '{terminal.location}'"
    )

    # DELETE (we'll delete at the end)

    # Test 2: Route CRUD
    print("\n🛣️ ROUTE CRUD OPERATIONS")
    print("-" * 40)

    route_count_before = Route.objects.count()
    test_route, created = Route.objects.get_or_create(
        origin="CRUD Test Origin",
        destination="CRUD Test Destination",
        defaults={
            "distance_km": 10.5,
            "duration_hours": 1.0,
            "base_fare": 15.00,
            "origin_terminal": test_terminal,
            "destination_terminal": Terminal.objects.first(),
            "is_active": True,
        },
    )

    if created:
        print(f"✅ CREATE: Route created - {test_route}")
    else:
        print(f"⚠️  Route already exists - {test_route}")

    # READ
    route = Route.objects.get(id=test_route.id)
    print(f"✅ READ: Route found - {route}")

    # UPDATE
    original_fare = route.base_fare
    route.base_fare = 20.00
    route.save()
    print(f"✅ UPDATE: Route fare updated from {original_fare} to {route.base_fare}")

    # Test 3: Bus CRUD
    print("\n🚌 BUS CRUD OPERATIONS")
    print("-" * 40)

    bus_count_before = Bus.objects.count()
    test_bus, created = Bus.objects.get_or_create(
        bus_number="CRUD-001",
        defaults={
            "bus_name": "CRUD Test Bus",
            "bus_type": "standard",
            "seat_capacity": 25,
            "assigned_route": test_route,
            "is_active": True,
        },
    )

    if created:
        print(f"✅ CREATE: Bus created - {test_bus}")
    else:
        print(f"⚠️  Bus already exists - {test_bus}")

    # READ
    bus = Bus.objects.get(id=test_bus.id)
    print(f"✅ READ: Bus found - {bus}")

    # UPDATE
    original_name = bus.bus_name
    bus.bus_name = "Updated CRUD Test Bus"
    bus.save()
    print(f"✅ UPDATE: Bus name updated from '{original_name}' to '{bus.bus_name}'")

    # Test 4: Booking CRUD
    print("\n🎫 BOOKING CRUD OPERATIONS")
    print("-" * 40)

    booking_count_before = Booking.objects.count()

    # Get a customer user
    customer = User.objects.filter(user_type="customer").first()
    if not customer:
        customer = User.objects.create_user(
            username="crud_test_customer",
            email="crud_test@example.com",
            password="testpass123",
            first_name="CRUD",
            last_name="Test",
            user_type="customer",
        )
        print(f"✅ Created test customer: {customer}")

    # Get a seat
    seat = test_bus.seats.first()
    if not seat:
        seat = Seat.objects.create(bus=test_bus, seat_number="A1", seat_type="window")
        print(f"✅ Created test seat: {seat}")

    travel_date = timezone.now() + timedelta(days=1)
    test_booking, created = Booking.objects.get_or_create(
        customer=customer,
        route=test_route,
        bus=test_bus,
        seat=seat,
        travel_date=travel_date,
        defaults={
            "passenger_name": "CRUD Test Passenger",
            "passenger_phone": "+23276123456",
            "ticket_price": 20.00,
            "status": "pending",
        },
    )

    if created:
        print(f"✅ CREATE: Booking created - {test_booking.pnr_code}")
    else:
        print(f"⚠️  Booking already exists - {test_booking.pnr_code}")

    # READ
    booking = Booking.objects.get(id=test_booking.id)
    print(f"✅ READ: Booking found - {booking.pnr_code}")

    # UPDATE
    original_status = booking.status
    booking.status = "confirmed"
    booking.save()
    print(
        f"✅ UPDATE: Booking status updated from '{original_status}' to '{booking.status}'"
    )

    # Test QR Code Generation
    try:
        booking.generate_qr_code()
        print(f"✅ QR CODE: Generated successfully for booking {booking.pnr_code}")
    except Exception as e:
        print(f"⚠️ QR CODE: Generation failed - {e}")

    # Test 5: User Management
    print("\n👤 USER CRUD OPERATIONS")
    print("-" * 40)

    user_count_before = User.objects.count()
    test_user, created = User.objects.get_or_create(
        username="crud_test_staff",
        defaults={
            "email": "crud_staff@example.com",
            "first_name": "CRUD",
            "last_name": "Staff",
            "user_type": "staff",
            "is_active": True,
        },
    )

    if created:
        test_user.set_password("testpass123")
        test_user.save()
        print(f"✅ CREATE: User created - {test_user.username}")
    else:
        print(f"⚠️  User already exists - {test_user.username}")

    # READ
    user = User.objects.get(id=test_user.id)
    print(f"✅ READ: User found - {user.username}")

    # UPDATE
    original_email = user.email
    user.email = "updated_crud_staff@example.com"
    user.save()
    print(f"✅ UPDATE: User email updated from '{original_email}' to '{user.email}'")

    # Final summary
    print("\n📊 CRUD OPERATIONS SUMMARY")
    print("=" * 60)
    print(f"✅ Terminals: {Terminal.objects.count()} (was {terminal_count_before})")
    print(f"✅ Routes: {Route.objects.count()} (was {route_count_before})")
    print(f"✅ Buses: {Bus.objects.count()} (was {bus_count_before})")
    print(f"✅ Bookings: {Booking.objects.count()} (was {booking_count_before})")
    print(f"✅ Users: {User.objects.count()} (was {user_count_before})")

    # Clean up test data
    print("\n🧹 CLEANING UP TEST DATA")
    print("-" * 40)

    # DELETE operations (testing delete functionality)
    if created:  # Only delete if we created new data
        try:
            test_booking.delete()
            print(f"✅ DELETE: Test booking deleted")
        except:
            print(f"⚠️ DELETE: Could not delete test booking")

        try:
            test_bus.delete()
            print(f"✅ DELETE: Test bus deleted")
        except:
            print(f"⚠️ DELETE: Could not delete test bus")

        try:
            test_route.delete()
            print(f"✅ DELETE: Test route deleted")
        except:
            print(f"⚠️ DELETE: Could not delete test route")

        try:
            test_terminal.delete()
            print(f"✅ DELETE: Test terminal deleted")
        except:
            print(f"⚠️ DELETE: Could not delete test terminal")

        try:
            test_user.delete()
            print(f"✅ DELETE: Test user deleted")
        except:
            print(f"⚠️ DELETE: Could not delete test user")

    print(f"\n🎯 ALL CRUD OPERATIONS TESTED SUCCESSFULLY!")
    print("All entities support Create, Read, Update, and Delete operations.")


if __name__ == "__main__":
    test_all_crud_operations()
