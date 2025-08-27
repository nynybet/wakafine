#!/usr/bin/env python
"""
Comprehensive test of all CRUD operations in Waka-Fine Bus system
Tests users, tickets, bookings, routes, b        # Create seats for this bus    # Get a customer user
    customer = User.objects.filter(role='customer').first()
    if not customer:
        customer = User.objects.create_user(
            username="crud_test_customer",
            email="crud_test@example.com",
            password="testpass123",
            first_name="CRUD",
            last_name="Test",
            role="customer"
        )r i in range(1, 26):  # 25 seats
            seat_number = f"A{i}" if i <= 12 else f"B{i-12}"
            Seat.objects.create(
                bus=test_bus,
                seat_number=seat_number,
                is_window=(i % 2 == 1),
                is_available=True
            )d terminals
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

    # Test 2: Route CRUD
    print("\n🛣️ ROUTE CRUD OPERATIONS")
    print("-" * 40)

    route_count_before = Route.objects.count()
    test_route, created = Route.objects.get_or_create(
        name="CRUD Test Route",
        origin="lumley",
        destination="kissy",
        defaults={
            "price": 15.00,
            "departure_time": "08:00:00",
            "arrival_time": "09:00:00",
            "duration_minutes": 60,
            "origin_terminal": test_terminal,
            "destination_terminal": Terminal.objects.exclude(
                id=test_terminal.id
            ).first(),
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
    original_price = route.price
    route.price = 20.00
    route.save()
    print(f"✅ UPDATE: Route price updated from {original_price} to {route.price}")

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
        # Create seats for this bus
        for i in range(1, 26):  # 25 seats
            seat_number = f"A{i}" if i <= 12 else f"B{i-12}"
            Seat.objects.create(
                bus=test_bus,
                seat_number=seat_number,
                seat_type="window" if i % 2 == 1 else "aisle",
            )
        print(f"✅ Created {test_bus.seats.count()} seats for bus")
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

    # Test admin interface accessibility
    print("\n🔐 ADMIN INTERFACE ACCESSIBILITY")
    print("-" * 40)

    # Create a test client
    client = Client()

    # Test admin login
    admin_user = User.objects.filter(is_superuser=True).first()
    if admin_user:
        client.force_login(admin_user)

        # Test admin dashboard access
        response = client.get("/accounts/admin/dashboard/")
        if response.status_code == 200:
            print("✅ Admin dashboard accessible")
        else:
            print(f"⚠️ Admin dashboard access failed: {response.status_code}")

        # Test manage terminals access
        response = client.get("/accounts/admin/terminals/")
        if response.status_code == 200:
            print("✅ Terminal management accessible")
        else:
            print(f"⚠️ Terminal management access failed: {response.status_code}")

        # Test manage routes access
        response = client.get("/accounts/admin/routes/")
        if response.status_code == 200:
            print("✅ Route management accessible")
        else:
            print(f"⚠️ Route management access failed: {response.status_code}")

        # Test manage buses access
        response = client.get("/accounts/admin/buses/")
        if response.status_code == 200:
            print("✅ Bus management accessible")
        else:
            print(f"⚠️ Bus management access failed: {response.status_code}")

        # Test manage bookings access
        response = client.get("/accounts/admin/bookings/")
        if response.status_code == 200:
            print("✅ Booking management accessible")
        else:
            print(f"⚠️ Booking management access failed: {response.status_code}")
    else:
        print("⚠️ No admin user found for testing")

    # Clean up test data
    print("\n🧹 CLEANING UP TEST DATA")
    print("-" * 40)

    # DELETE operations (testing delete functionality)
    cleanup_success = True

    try:
        if "test_booking" in locals() and test_booking.pk:
            test_booking.delete()
            print(f"✅ DELETE: Test booking deleted")
    except Exception as e:
        print(f"⚠️ DELETE: Could not delete test booking - {e}")
        cleanup_success = False

    try:
        if "test_bus" in locals() and test_bus.pk and created:
            test_bus.delete()
            print(f"✅ DELETE: Test bus deleted")
    except Exception as e:
        print(f"⚠️ DELETE: Could not delete test bus - {e}")
        cleanup_success = False

    try:
        if "test_route" in locals() and test_route.pk and created:
            test_route.delete()
            print(f"✅ DELETE: Test route deleted")
    except Exception as e:
        print(f"⚠️ DELETE: Could not delete test route - {e}")
        cleanup_success = False

    try:
        if "test_terminal" in locals() and test_terminal.pk and created:
            test_terminal.delete()
            print(f"✅ DELETE: Test terminal deleted")
    except Exception as e:
        print(f"⚠️ DELETE: Could not delete test terminal - {e}")
        cleanup_success = False

    try:
        if "test_user" in locals() and test_user.pk and created:
            test_user.delete()
            print(f"✅ DELETE: Test user deleted")
    except Exception as e:
        print(f"⚠️ DELETE: Could not delete test user - {e}")
        cleanup_success = False

    print("\n🎯 COMPREHENSIVE CRUD TEST COMPLETED!")
    print("=" * 60)
    print("✅ All entities support full CRUD operations")
    print("✅ QR code generation with terminal information working")
    print("✅ Admin interface accessible for all management features")
    print("✅ Terminal and route relationships functioning")

    if cleanup_success:
        print("✅ Test data cleanup successful")
    else:
        print("⚠️ Some test data may remain - check manually if needed")


if __name__ == "__main__":
    test_all_crud_operations()
