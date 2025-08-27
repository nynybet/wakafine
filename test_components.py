#!/usr/bin/env python
"""
Test PDF generation and AJAX functionality separately
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


def test_pdf_generation():
    """Test PDF generation functionality"""
    print("TESTING PDF GENERATION")
    print("=" * 30)

    client = Client()
    client.login(username="customer", password="customer123")

    # Get a recent booking
    booking = Booking.objects.filter(customer__username="customer").first()
    if not booking:
        print("❌ No booking found for customer")
        return False

    print(f"Testing PDF for booking: {booking.pnr_code}")

    try:
        pdf_url = reverse("bookings:ticket_pdf", kwargs={"pk": booking.pk})
        print(f"PDF URL: {pdf_url}")

        pdf_response = client.get(pdf_url)
        print(f"PDF Response Status: {pdf_response.status_code}")

        if pdf_response.status_code == 200:
            content_type = pdf_response.get("Content-Type")
            content_length = len(pdf_response.content)
            print(f"✅ PDF Generated Successfully!")
            print(f"   Content Type: {content_type}")
            print(f"   Size: {content_length} bytes")
            return True
        else:
            print(f"❌ PDF Generation Failed")
            return False

    except Exception as e:
        print(f"❌ PDF Error: {str(e)}")
        return False


def test_ajax_endpoint():
    """Test AJAX seat availability endpoint"""
    print("\nTESTING AJAX SEAT AVAILABILITY")
    print("=" * 35)

    client = Client()

    # Get test data
    route = Route.objects.first()
    bus = Bus.objects.filter(assigned_route=route).first()
    travel_date = (timezone.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    print(f"Testing with Bus ID: {bus.id}")
    print(f"Travel Date: {travel_date}")

    try:
        # Test the AJAX endpoint
        ajax_url = (
            f"/bookings/seat-availability/?bus_id={bus.id}&travel_date={travel_date}"
        )
        print(f"AJAX URL: {ajax_url}")

        ajax_response = client.get(ajax_url)
        print(f"AJAX Response Status: {ajax_response.status_code}")

        if ajax_response.status_code == 200:
            try:
                data = json.loads(ajax_response.content)
                print(f"✅ AJAX Working!")
                print(f"   Available Seats: {data.get('available_seats', 'N/A')}")
                print(f"   Total Seats: {data.get('total_seats', 'N/A')}")
                print(f"   Bus Name: {data.get('bus_name', 'N/A')}")
                return True
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON response")
                print(f"   Content: {ajax_response.content[:100]}")
                return False
        else:
            print(f"❌ AJAX Failed")
            print(f"   Content: {ajax_response.content[:200]}")
            return False

    except Exception as e:
        print(f"❌ AJAX Error: {str(e)}")
        return False


def test_qr_functionality():
    """Test QR code functionality"""
    print("\nTESTING QR CODE FUNCTIONALITY")
    print("=" * 35)

    # Get a recent booking
    booking = Booking.objects.first()
    if not booking:
        print("❌ No booking found")
        return False

    print(f"Testing QR for booking: {booking.pnr_code}")

    if booking.qr_code:
        print(f"✅ QR Code exists: {booking.qr_code.url}")

        # Check if file exists
        try:
            qr_path = booking.qr_code.path
            if os.path.exists(qr_path):
                file_size = os.path.getsize(qr_path)
                print(f"✅ QR Code file found. Size: {file_size} bytes")
                return True
            else:
                print(f"⚠️ QR Code URL exists but file not found")
                return False
        except Exception as e:
            print(f"⚠️ QR Code path error: {str(e)}")
            return False
    else:
        print("❌ QR Code not generated")
        return False


if __name__ == "__main__":
    pdf_ok = test_pdf_generation()
    ajax_ok = test_ajax_endpoint()
    qr_ok = test_qr_functionality()

    print("\n" + "=" * 50)
    print("COMPONENT TEST SUMMARY:")
    print(f"PDF Generation: {'✅ Working' if pdf_ok else '❌ Issues'}")
    print(f"AJAX Endpoint: {'✅ Working' if ajax_ok else '❌ Issues'}")
    print(f"QR Code: {'✅ Working' if qr_ok else '❌ Issues'}")

    if pdf_ok and ajax_ok and qr_ok:
        print("\n🎉 All components working correctly!")
    else:
        print("\n⚠️ Some components need attention.")
