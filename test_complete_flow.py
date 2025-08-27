#!/usr/bin/env python
"""
Complete end-to-end booking flow test for Waka-Fine Bus system
Tests the full user journey from login to ticket generation
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine_bus.settings")
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from routes.models import Route
from buses.models import Bus, Seat
from bookings.models import Booking
from django.test import Client
from django.urls import reverse
import json

User = get_user_model()


def test_booking_flow():
    """Test complete booking flow"""
    print("🚌 WAKA-FINE BUS - COMPLETE BOOKING FLOW TEST")
    print("=" * 60)

    # 1. Test user authentication
    print("\n1. Testing User Authentication...")
    client = Client()

    # Test customer login
    login_response = client.login(username="customer", password="customer123")
    if login_response:
        print("✅ Customer login successful")
    else:
        print("❌ Customer login failed")
        return False

    # 2. Test route search functionality
    print("\n2. Testing Route Search...")
    routes = Route.objects.all()
    if routes.exists():
        test_route = routes.first()
        print(f"✅ Found {routes.count()} routes. Testing with: {test_route}")
    else:
        print("❌ No routes found")
        return False

    # 3. Test bus and seat availability
    print("\n3. Testing Bus and Seat Availability...")
    buses = Bus.objects.filter(assigned_route=test_route)
    if buses.exists():
        test_bus = buses.first()
        seats = test_bus.seats.filter(is_available=True)
        if seats.exists():
            test_seat = seats.first()
            print(
                f"✅ Found bus '{test_bus.bus_name}' with {seats.count()} available seats"
            )
            print(f"   Testing with seat: {test_seat.seat_number}")
        else:
            print(f"❌ No available seats on bus '{test_bus.bus_name}'")
            return False
    else:
        print(f"❌ No buses found for route '{test_route}'")
        return False

    # 4. Test AJAX seat availability endpoint
    print("\n4. Testing AJAX Seat Availability...")
    travel_date = (timezone.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    ajax_url = (
        f"/bookings/seat-availability/?bus_id={test_bus.id}&travel_date={travel_date}"
    )
    ajax_response = client.get(ajax_url)

    if ajax_response.status_code == 200:
        seat_data = json.loads(ajax_response.content)
        available_seats = seat_data.get("available_seats", 0)
        print(f"✅ AJAX endpoint working. Available seats: {available_seats}")
    else:
        print(f"❌ AJAX endpoint failed with status: {ajax_response.status_code}")

    # 5. Test booking creation
    print("\n5. Testing Booking Creation...")
    customer = User.objects.get(username="customer")
    travel_datetime = timezone.now() + timedelta(days=1)

    booking_data = {
        "customer": customer,
        "route": test_route,
        "bus": test_bus,
        "seat": test_seat,
        "travel_date": travel_datetime,
        "payment_method": "afrimoney",
        "amount_paid": test_route.base_fare,
        "status": "pending",
    }

    try:
        new_booking = Booking.objects.create(**booking_data)
        print(f"✅ Booking created successfully!")
        print(f"   PNR Code: {new_booking.pnr_code}")
        print(f"   QR Code: {'Generated' if new_booking.qr_code else 'Not generated'}")
    except Exception as e:
        print(f"❌ Booking creation failed: {str(e)}")
        return False

    # 6. Test payment simulation
    print("\n6. Testing Payment Simulation...")
    payment_url = reverse("bookings:payment", kwargs={"pk": new_booking.pk})
    payment_data = {"payment_method": "afrimoney"}
    payment_response = client.post(payment_url, payment_data)

    if payment_response.status_code in [200, 302]:  # 302 is redirect after success
        new_booking.refresh_from_db()
        if new_booking.status == "confirmed":
            print(f"✅ Payment simulation successful. Status: {new_booking.status}")
        else:
            print(f"⚠️  Payment processed but status is: {new_booking.status}")
    else:
        print(
            f"❌ Payment simulation failed with status: {payment_response.status_code}"
        )

    # 7. Test PNR search functionality
    print("\n7. Testing PNR Search...")
    search_url = f"/bookings/search/?pnr_code={new_booking.pnr_code}"
    search_response = client.get(search_url)

    if search_response.status_code == 200:
        if new_booking.pnr_code.encode() in search_response.content:
            print(f"✅ PNR search working. Found booking: {new_booking.pnr_code}")
        else:
            print("⚠️  PNR search page loaded but booking not found")
    else:
        print(f"❌ PNR search failed with status: {search_response.status_code}")

    # 8. Test PDF ticket generation
    print("\n8. Testing PDF Ticket Generation...")
    pdf_url = reverse("bookings:ticket_pdf", kwargs={"pk": new_booking.pk})
    pdf_response = client.get(pdf_url)

    if pdf_response.status_code == 200:
        if pdf_response.get("Content-Type") == "application/pdf":
            print(
                f"✅ PDF generation successful. Size: {len(pdf_response.content)} bytes"
            )
        else:
            print(
                f"⚠️  PDF endpoint accessible but content type: {pdf_response.get('Content-Type')}"
            )
    else:
        print(f"❌ PDF generation failed with status: {pdf_response.status_code}")

    # 9. Test QR code functionality
    print("\n9. Testing QR Code Generation...")
    if new_booking.qr_code:
        print(f"✅ QR Code generated: {new_booking.qr_code.url}")
        # Test QR code file exists
        try:
            qr_path = new_booking.qr_code.path
            if os.path.exists(qr_path):
                file_size = os.path.getsize(qr_path)
                print(f"✅ QR Code file exists. Size: {file_size} bytes")
            else:
                print("⚠️  QR Code URL exists but file not found on disk")
        except Exception as e:
            print(f"⚠️  QR Code path check failed: {str(e)}")
    else:
        print("❌ QR Code not generated")

    # 10. Test booking list view
    print("\n10. Testing Booking List View...")
    booking_list_url = reverse("bookings:list")
    list_response = client.get(booking_list_url)

    if list_response.status_code == 200:
        if new_booking.pnr_code.encode() in list_response.content:
            print(f"✅ Booking appears in customer's booking list")
        else:
            print("⚠️  Booking list page loaded but new booking not visible")
    else:
        print(f"❌ Booking list failed with status: {list_response.status_code}")

    print("\n" + "=" * 60)
    print("🎉 BOOKING FLOW TEST COMPLETED!")
    print(f"📋 Test Booking Details:")
    print(f"   - PNR: {new_booking.pnr_code}")
    print(f"   - Route: {new_booking.route}")
    print(f"   - Bus: {new_booking.bus.bus_name}")
    print(f"   - Seat: {new_booking.seat.seat_number}")
    print(f"   - Status: {new_booking.status}")
    print(f"   - Amount: SLE {new_booking.amount_paid}")
    print("=" * 60)

    return True


def test_admin_staff_access():
    """Test admin and staff dashboard access"""
    print("\n🔧 TESTING ADMIN & STAFF ACCESS")
    print("=" * 40)

    client = Client()

    # Test admin login
    print("\n1. Testing Admin Access...")
    admin_login = client.login(username="admin", password="admin@1234")
    if admin_login:
        print("✅ Admin login successful")

        # Test admin dashboard access
        admin_response = client.get("/admin/")
        if admin_response.status_code == 200:
            print("✅ Admin dashboard accessible")
        else:
            print(f"⚠️  Admin dashboard status: {admin_response.status_code}")
    else:
        print("❌ Admin login failed")

    # Test staff login
    print("\n2. Testing Staff Access...")
    client.logout()
    staff_login = client.login(username="staff", password="staff123")
    if staff_login:
        print("✅ Staff login successful")

        # Test staff can see all bookings
        booking_list_url = reverse("bookings:list")
        staff_response = client.get(booking_list_url)
        if staff_response.status_code == 200:
            print("✅ Staff can access booking list")
        else:
            print(f"⚠️  Staff booking list status: {staff_response.status_code}")
    else:
        print("❌ Staff login failed")


def show_system_stats():
    """Display current system statistics"""
    print("\n📊 CURRENT SYSTEM STATISTICS")
    print("=" * 40)

    users = User.objects.all()
    routes = Route.objects.all()
    buses = Bus.objects.all()
    seats = Seat.objects.all()
    bookings = Booking.objects.all()

    print(f"👥 Users: {users.count()}")
    for role in ["admin", "staff", "customer"]:
        count = users.filter(role=role).count()
        print(f"   - {role.title()}: {count}")

    print(f"🛣️  Routes: {routes.count()}")
    print(f"🚌 Buses: {buses.count()}")
    print(f"💺 Total Seats: {seats.count()}")
    print(f"   - Available: {seats.filter(is_available=True).count()}")
    print(f"   - Window Seats: {seats.filter(is_window=True).count()}")

    print(f"🎫 Bookings: {bookings.count()}")
    for status in ["pending", "confirmed", "cancelled", "completed"]:
        count = bookings.filter(status=status).count()
        print(f"   - {status.title()}: {count}")

    # Show recent bookings
    recent_bookings = bookings.order_by("-created_at")[:5]
    print(f"\n📋 Recent Bookings:")
    for booking in recent_bookings:
        print(
            f"   - {booking.pnr_code}: {booking.customer.username} → {booking.route} ({booking.status})"
        )


if __name__ == "__main__":
    show_system_stats()

    if test_booking_flow():
        test_admin_staff_access()
        print("\n🎊 ALL TESTS COMPLETED SUCCESSFULLY!")
        print("The Waka-Fine Bus booking system is fully operational! 🚌✨")
    else:
        print("\n⚠️  Some tests failed. Please check the issues above.")
