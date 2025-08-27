#!/usr/bin/env python
"""
Test script to verify all ticket functionality URLs are working
"""
import os
import sys
import django
from django.test import Client
from django.urls import reverse

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine_bus.settings")
django.setup()

from bookings.models import Booking


def test_ticket_urls():
    """Test all ticket-related URLs"""
    client = Client()

    # Get the latest booking
    booking = Booking.objects.last()
    if not booking:
        print("❌ No bookings found. Please create a test booking first.")
        return False

    print(f"🎫 Testing ticket functionality for booking ID: {booking.id}")
    print(f"📝 PNR: {booking.pnr_code}")
    print(f"👤 Customer: {booking.customer.username}")
    print("=" * 60)

    # Test URLs
    test_cases = [
        {
            "name": "Payment Success Page",
            "url": f"/bookings/payment/success/{booking.id}/",
            "expected_status": 200,
        },
        {
            "name": "Ticket View (Main)",
            "url": f"/bookings/{booking.id}/ticket/",
            "expected_status": 200,
        },
        {
            "name": "Ticket Print View",
            "url": f"/bookings/{booking.id}/ticket/print/",
            "expected_status": 200,
        },
        {
            "name": "Ticket PDF View",
            "url": f"/bookings/{booking.id}/ticket/pdf/",
            "expected_status": 200,
        },
    ]

    all_passed = True

    for test in test_cases:
        try:
            print(f"🔄 Testing {test['name']}...")
            print(f"   URL: {test['url']}")

            response = client.get(test["url"])

            if response.status_code == test["expected_status"]:
                print(f"   ✅ SUCCESS - Status: {response.status_code}")

                # Check for specific content based on the view
                if "payment/success" in test["url"]:
                    if booking.pnr_code.encode() in response.content:
                        print("   ✅ PNR code found in payment success page")
                    else:
                        print("   ⚠️  PNR code not found in response")

                elif "ticket/print" in test["url"]:
                    if (
                        b"QR Code" in response.content
                        and b"Print Ticket" in response.content
                    ):
                        print("   ✅ Print ticket elements found")
                    else:
                        print("   ⚠️  Print ticket elements missing")

                elif "ticket/pdf" in test["url"]:
                    if response.headers.get("Content-Type") == "application/pdf":
                        print("   ✅ PDF content type correct")
                    else:
                        print(
                            f"   ⚠️  Content type: {response.headers.get('Content-Type')}"
                        )

                elif "/ticket/" in test["url"]:
                    if booking.pnr_code.encode() in response.content:
                        print("   ✅ Ticket content found")
                    else:
                        print("   ⚠️  Ticket content missing")

            else:
                print(
                    f"   ❌ FAILED - Status: {response.status_code} (Expected: {test['expected_status']})"
                )
                all_passed = False

        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            all_passed = False

        print()

    print("=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Ticket functionality is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")

    return all_passed


if __name__ == "__main__":
    test_ticket_urls()
