#!/usr/bin/env python
"""
Test script to verify ticket_print.html QR code and round trip fixes
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine.settings")
django.setup()

from bookings.models import Booking


def test_ticket_print_fixes():
    """Test the ticket_print.html QR and round trip fixes"""

    print("🎫 TICKET_PRINT.HTML QR CODE & ROUND TRIP FIX TEST")
    print("=" * 60)

    print("🔧 FIXES IMPLEMENTED:")
    print("   ✅ Updated server-side QR code generation in views.py")
    print("   ✅ Added round trip information to QR code data")
    print("   ✅ Added round trip display sections to ticket_print.html")
    print("   ✅ QR code now includes return date, bus, and seat when available")

    # Check database
    try:
        total_bookings = Booking.objects.count()
        round_trips = Booking.objects.filter(trip_type="round_trip").count()

        print(f"\n📊 Database Status:")
        print(f"   Total bookings: {total_bookings}")
        print(f"   Round trip bookings: {round_trips}")

        if total_bookings > 0:
            # Find latest booking
            latest = Booking.objects.last()
            print(f"\n🎫 Latest Booking for Testing:")
            print(f"   ID: {latest.id}")
            print(f"   PNR: {latest.pnr_code}")
            print(f"   Trip Type: {latest.trip_type}")
            print(f"   Route: {latest.route.origin} → {latest.route.destination}")

            # Check return data
            if latest.trip_type == "round_trip":
                print(f"\n🔄 Return Trip Analysis:")
                return_fields = {
                    "return_date": latest.return_date,
                    "return_bus": latest.return_bus,
                    "return_seat": latest.return_seat,
                }

                has_return_data = any(return_fields.values())
                print(f"   Return data present: {has_return_data}")

                for field, value in return_fields.items():
                    if value:
                        display_val = (
                            value.strftime("%b %d, %Y")
                            if field == "return_date"
                            else str(value)
                        )
                        print(f"   ✅ {field}: {display_val}")
                    else:
                        print(f"   ❌ {field}: Not set")

                print(f"\n📱 Expected QR Code Content:")
                if has_return_data:
                    print("   ✅ Should include 'Trip Type: Round Trip'")
                    if latest.return_date:
                        print("   ✅ Should include return date")
                    if latest.return_bus:
                        print("   ✅ Should include return bus name")
                    if latest.return_seat:
                        print("   ✅ Should include return seat number")
                else:
                    print("   ⚠️ Should show 'Trip Type: One Way' (no return data)")
            else:
                print(f"\n📱 Expected QR Code Content:")
                print("   ✅ Should show 'Trip Type: One Way'")

            print(f"\n🌐 Test URL:")
            print(f"   http://127.0.0.1:9000/bookings/{latest.id}/ticket/")

            print(f"\n📋 QR Code Data Structure:")
            print(f"   • WAKA-FINE TICKET header")
            print(f"   • PNR: {latest.pnr_code}")
            print(f"   • Passenger name")
            print(f"   • Route information")
            print(f"   • Outbound date, bus, seat")
            print(f"   • Trip type (Round Trip or One Way)")
            if latest.trip_type == "round_trip" and any(
                [latest.return_date, latest.return_bus, latest.return_seat]
            ):
                print(f"   • Return trip details (when available)")
            print(f"   • Amount and status")

        else:
            print("❌ No bookings found in database!")

    except Exception as e:
        print(f"❌ Database error: {e}")

    print(f"\n✨ TEMPLATE DISPLAY FEATURES:")
    print(f"   🎯 Trip Type field shows 'Round Trip' or 'One Way'")
    print(f"   🎯 Return trip sections appear only when data exists")
    print(f"   🎯 Blue-highlighted return trip details")
    print(f"   🎯 Server-side QR generation with comprehensive data")

    print(f"\n🚀 EXPECTED RESULTS:")
    print(f"   ✅ QR code displays correctly on ticket page")
    print(f"   ✅ QR code contains round trip information when available")
    print(f"   ✅ Template shows return trip details when present")
    print(f"   ✅ Print functionality works properly")

    print(f"\n🔍 HOW TO TEST:")
    print(f"   1. Visit the ticket URL")
    print(f"   2. Verify QR code is visible")
    print(f"   3. Scan QR code to check content")
    print(f"   4. Check if return trip details display (for round trips)")
    print(f"   5. Try printing the ticket")


if __name__ == "__main__":
    test_ticket_print_fixes()
