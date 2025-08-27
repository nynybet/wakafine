#!/usr/bin/env python3
"""
Live test for QR code in print view using development server
"""

import os
import sys
import time
import threading
import subprocess
import requests
from urllib.parse import urljoin
import django
from django.conf import settings

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine_bus.settings")
django.setup()

from bookings.models import Booking


def start_dev_server():
    """Start Django development server in background"""
    cmd = [sys.executable, "manage.py", "runserver", "127.0.0.1:8001", "--noreload"]
    return subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=os.path.dirname(os.path.abspath(__file__)),
    )


def test_live_qr():
    """Test QR code generation in live server"""

    print("🚀 Starting live QR test...")

    # Get a sample booking
    try:
        booking = Booking.objects.filter(status="confirmed").first()
        if not booking:
            print("❌ No confirmed bookings found")
            return False

        print(f"✅ Found booking: {booking.pnr_code}")

        # Start development server
        print("🖥️ Starting development server...")
        server_process = start_dev_server()

        # Wait for server to start
        time.sleep(3)

        try:
            # Test server availability
            base_url = "http://127.0.0.1:8001"
            health_check = requests.get(base_url, timeout=5)

            if health_check.status_code == 200:
                print("✅ Development server running")

                # Test print view
                print_url = f"{base_url}/bookings/{booking.id}/ticket/print/"
                print(f"🔗 Testing: {print_url}")

                response = requests.get(print_url, timeout=10)

                if response.status_code == 200:
                    print("✅ Print view accessible")

                    # Check response content
                    content = response.text

                    # Critical checks for QR functionality
                    checks = [
                        ("QR container div", 'id="qr-code"' in content),
                        ("QR library script", "qrcode.min.js" in content),
                        ("Booking PNR", booking.pnr_code in content),
                        ("QR generation script", "QRCode.toCanvas" in content),
                        ("Print CSS", "@media print" in content),
                        ("Color adjustment", "print-color-adjust: exact" in content),
                        ("QR fallback", "qr-fallback" in content),
                        ("Error handling", "showFallback" in content),
                    ]

                    all_passed = True
                    for check_name, passed in checks:
                        status = "✅" if passed else "❌"
                        print(f"{status} {check_name}: {'PASS' if passed else 'FAIL'}")
                        if not passed:
                            all_passed = False

                    # Test auto-print variant
                    autoprint_url = f"{print_url}?autoprint=true"
                    autoprint_response = requests.get(autoprint_url, timeout=10)

                    if autoprint_response.status_code == 200:
                        print("✅ Auto-print URL accessible")

                        # Check that autoprint is enabled in context
                        if "autoprint" in autoprint_response.text:
                            print("✅ Auto-print context enabled")
                        else:
                            print("⚠️ Auto-print context may not be set")
                    else:
                        print(
                            f"❌ Auto-print URL failed: {autoprint_response.status_code}"
                        )
                        all_passed = False

                    if all_passed:
                        print("\n🎯 QR FUNCTIONALITY VERIFICATION:")
                        print(f"   📱 QR Code should be visible at: {print_url}")
                        print(f"   🖨️ Auto-print available at: {autoprint_url}")
                        print(
                            "   💡 Open these URLs in browser to manually verify QR visibility"
                        )

                    return all_passed

                else:
                    print(f"❌ Print view failed: HTTP {response.status_code}")
                    return False

            else:
                print(f"❌ Server not responding: HTTP {health_check.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return False

        finally:
            # Cleanup server
            if server_process:
                print("🛑 Stopping development server...")
                server_process.terminate()
                server_process.wait()

    except Exception as e:
        print(f"❌ Error in live test: {e}")
        return False


def main():
    """Main test function"""
    print("🔥 QR Code Live Print Test")
    print("=" * 60)

    success = test_live_qr()

    print("=" * 60)
    if success:
        print("🎉 QR code print view is properly configured!")
        print("🔍 Manual verification recommended:")
        print("   1. Run: python manage.py runserver")
        print("   2. Visit: /bookings/<id>/ticket/print/")
        print("   3. Check QR code appears (not just text)")
        print("   4. Test print preview (Ctrl+P)")
    else:
        print("💥 QR code setup has issues that need fixing")

    return success


if __name__ == "__main__":
    main()
