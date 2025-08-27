#!/usr/bin/env python
"""
Comprehensive test of terminal functionality in Waka-Fine Bus system
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine_bus.settings")
django.setup()

from terminals.models import Terminal
from routes.models import Route
from bookings.models import Booking
from buses.models import Bus, Seat
from accounts.models import User


def test_terminal_functionality():
    """Test all terminal functionality"""
    print("🧪 TESTING TERMINAL FUNCTIONALITY")
    print("=" * 50)

    # Test 1: Terminal CRUD operations
    print("\n1️⃣ Testing Terminal CRUD Operations")
    print("-" * 40)

    # Create
    print("Creating test terminal...")
    test_terminal, created = Terminal.objects.get_or_create(
        name="Test Terminal",
        defaults={
            "terminal_type": "bus_stop",
            "location": "Test Location",
            "city": "freetown",
            "operating_hours_start": "06:00:00",
            "operating_hours_end": "20:00:00",
            "is_active": True,
        },
    )
    print(f"✅ {'Created' if created else 'Found'}: {test_terminal}")

    # Read
    terminals = Terminal.objects.all()
    print(f"✅ Total terminals: {terminals.count()}")

    # Update
    test_terminal.description = "Updated description"
    test_terminal.save()
    print(f"✅ Updated terminal description")

    # Test 2: Terminal-Route relationships
    print("\n2️⃣ Testing Terminal-Route Relationships")
    print("-" * 40)

    routes_with_terminals = Route.objects.filter(
        origin_terminal__isnull=False, destination_terminal__isnull=False
    )
    print(f"✅ Routes with both terminals: {routes_with_terminals.count()}")

    for route in routes_with_terminals[:3]:
        print(f"   • {route.origin_terminal.name} → {route.destination_terminal.name}")
        print(f"     Route: {route}")

    # Test 3: Terminal statistics
    print("\n3️⃣ Testing Terminal Statistics")
    print("-" * 40)

    terminal_stats = {}
    for terminal_type, display_name in Terminal.TERMINAL_TYPE_CHOICES:
        count = Terminal.objects.filter(terminal_type=terminal_type).count()
        terminal_stats[display_name] = count
        print(f"✅ {display_name}: {count}")

    # Test by city
    print("\nBy City:")
    for city, display_name in Terminal.CITY_CHOICES:
        count = Terminal.objects.filter(city=city).count()
        if count > 0:
            print(f"✅ {display_name}: {count}")

    # Test 4: QR Code with terminal information
    print("\n4️⃣ Testing QR Code Generation with Terminal Info")
    print("-" * 40)

    # Find a booking to test
    booking = Booking.objects.first()
    if booking:
        print(f"✅ Testing with booking: {booking.pnr_code}")
        print(f"   Route: {booking.route}")
        if booking.route.origin_terminal:
            print(f"   Origin Terminal: {booking.route.origin_terminal.name}")
        if booking.route.destination_terminal:
            print(f"   Destination Terminal: {booking.route.destination_terminal.name}")

        # Test QR code generation
        if hasattr(booking, "generate_qr_code"):
            try:
                booking.generate_qr_code()
                print(f"✅ QR code generated successfully")
                if booking.qr_code:
                    print(f"   QR code file: {booking.qr_code.url}")
            except Exception as e:
                print(f"⚠️ QR code generation error: {e}")
    else:
        print("⚠️ No bookings found to test QR code")

    # Test 5: Terminal operating hours and facilities
    print("\n5️⃣ Testing Terminal Details")
    print("-" * 40)

    active_terminals = Terminal.objects.filter(is_active=True)[:5]
    for terminal in active_terminals:
        print(f"🏢 {terminal.name}")
        print(f"   Type: {terminal.get_terminal_type_display()}")
        print(f"   Location: {terminal.full_address}")
        print(f"   Hours: {terminal.operating_hours}")
        if terminal.facilities_list:
            print(f"   Facilities: {', '.join(terminal.facilities_list[:3])}...")

    # Test 6: Route terminal display
    print("\n6️⃣ Testing Route Terminal Display")
    print("-" * 40)

    routes = Route.objects.all()[:3]
    for route in routes:
        print(f"🛣️ {route}")
        print(f"   Origin Display: {route.origin_display}")
        print(f"   Destination Display: {route.destination_display}")
        if route.origin_terminal:
            print(
                f"   Origin Routes: {route.origin_terminal.get_routes_as_origin().count()}"
            )
        if route.destination_terminal:
            print(
                f"   Dest Routes: {route.destination_terminal.get_routes_as_destination().count()}"
            )

    # Clean up test terminal
    if created:
        test_terminal.delete()
        print(f"\n🧹 Cleaned up test terminal")

    # Final summary
    print("\n📊 TERMINAL SYSTEM SUMMARY")
    print("=" * 50)
    print(f"✅ Total Terminals: {Terminal.objects.count()}")
    print(f"✅ Active Terminals: {Terminal.objects.filter(is_active=True).count()}")
    print(
        f"✅ Routes with Terminals: {Route.objects.filter(origin_terminal__isnull=False).count()}"
    )
    print(f"✅ Total Bookings: {Booking.objects.count()}")

    print(f"\n🎯 All terminal functionality tests completed!")


if __name__ == "__main__":
    test_terminal_functionality()
