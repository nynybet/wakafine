#!/usr/bin/env python
import requests
import os
import sys


def test_views_browser():
    """Test views by making HTTP requests to running Django server"""

    base_url = "http://127.0.0.1:8000"
    booking_id = 21

    # Create session for cookies
    session = requests.Session()

    print("🎫 Testing ticket views via HTTP...")
    print(f"🌐 Server: {base_url}")
    print(f"📝 Booking ID: {booking_id}")

    # Test URLs
    test_urls = [
        f"/bookings/payment/success/{booking_id}/",
        f"/bookings/{booking_id}/ticket/",
        f"/bookings/{booking_id}/ticket/print/",
        f"/bookings/{booking_id}/ticket/pdf/",
    ]

    for url in test_urls:
        full_url = base_url + url
        print(f"\n🔄 Testing: {url}")
        try:
            response = session.get(full_url, timeout=5)
            print(f"📊 Status: {response.status_code}")

            if response.status_code == 200:
                print("✅ SUCCESS")
                # Check content length
                print(f"📄 Content length: {len(response.text)} chars")
                # Check if contains PNR
                if "FZ7INGHD" in response.text:
                    print("✅ Contains expected PNR code")
                else:
                    print("⚠️  PNR code not found in response")

            elif response.status_code == 302:
                print("🔄 REDIRECT")
                location = response.headers.get("Location", "Unknown")
                print(f"   → {location}")

            elif response.status_code == 404:
                print("❌ NOT FOUND")

            else:
                print(f"⚠️  Unexpected status: {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"❌ ERROR: {e}")

    print("\n" + "=" * 60)
    print("Note: 302 redirects are expected for unauthenticated requests")
    print("404 errors might indicate URL pattern issues")


if __name__ == "__main__":
    test_views_browser()
