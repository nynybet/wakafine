#!/usr/bin/env python3
"""
Simple currency update script for Sierra Leone redenomination
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine_bus.settings")
django.setup()

from routes.models import Route
from bookings.models import Booking
from decimal import Decimal

print("=== Currency Redenomination Update ===")

try:
    # Check current routes
    routes = Route.objects.all()
    print(f"Found {routes.count()} routes")

    if routes.count() > 0:
        print("\nBefore update:")
        for route in routes[:3]:
            print(f"  {route.name}: Le {route.price}")

        # Update each route
        for route in routes:
            old_price = float(route.price)
            # Convert thousands to tens (divide by 1000, minimum Le 5)
            new_price = max(5, int(old_price / 1000))

            route.price = Decimal(str(new_price))
            route.save()
            print(f"Updated {route.name}: Le {old_price:,.0f} → Le {new_price}")

        print(f"\n✅ Updated {routes.count()} routes")

    # Check bookings
    bookings = Booking.objects.all()
    print(f"\nFound {bookings.count()} bookings")

    if bookings.count() > 0:
        # Update each booking
        for booking in bookings:
            old_amount = float(booking.total_amount)
            # Convert thousands to tens
            new_amount = max(5, int(old_amount / 1000))

            booking.total_amount = Decimal(str(new_amount))
            booking.amount_paid = Decimal(str(new_amount))
            booking.save()
            print(
                f"Updated booking {booking.pnr_code}: Le {old_amount:,.0f} → Le {new_amount}"
            )

        print(f"\n✅ Updated {bookings.count()} bookings")

    print("\n🎉 Currency update completed!")

except Exception as e:
    print(f"Error: {e}")
    import traceback

    traceback.print_exc()
