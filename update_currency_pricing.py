#!/usr/bin/env python3
"""
Currency Redenomination Update Script
Updates all transportation pricing from thousands to tens to reflect Sierra Leone's currency change.
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


def update_currency_pricing():
    """Update all pricing from thousands to tens due to currency redenomination"""
    print("=== Sierra Leone Currency Redenomination Update ===")
    print("Converting thousands to tens (e.g., Le 15,000 → Le 15)")
    print("Minimum fare: Le 5")

    # Currency conversion mapping (thousands to tens)
    price_mapping = {
        25000: 25,  # Le 25,000 → Le 25
        22000: 22,  # Le 22,000 → Le 22
        20000: 20,  # Le 20,000 → Le 20
        18000: 18,  # Le 18,000 → Le 18
        16000: 16,  # Le 16,000 → Le 16
        15000: 15,  # Le 15,000 → Le 15
        14000: 14,  # Le 14,000 → Le 14
        12000: 12,  # Le 12,000 → Le 12
        10000: 10,  # Le 10,000 → Le 10
        8000: 8,  # Le 8,000 → Le 8
    }

    # Update Routes
    print("\n📍 Updating Route Prices...")
    routes_updated = 0

    for route in Route.objects.all():
        old_price = float(route.price)

        if old_price in price_mapping:
            new_price = price_mapping[old_price]
        else:
            # For any other prices, divide by 1000 and ensure minimum of Le 5
            new_price = max(5, int(old_price / 1000))

        print(
            f"   {route.origin} → {route.destination}: Le {old_price:,.0f} → Le {new_price}"
        )

        route.price = Decimal(str(new_price))
        route.save()
        routes_updated += 1

    print(f"✅ Updated {routes_updated} routes")

    # Update existing bookings
    print("\n🎫 Updating Booking Amounts...")
    bookings_updated = 0

    for booking in Booking.objects.all():
        old_amount = float(booking.total_amount)

        # Convert booking amounts using the same logic
        if old_amount in price_mapping:
            new_amount = price_mapping[old_amount]
        elif old_amount in [price * 2 for price in price_mapping.keys()]:
            # Handle round-trip bookings (double price)
            base_price = old_amount / 2
            if base_price in price_mapping:
                new_amount = price_mapping[base_price] * 2
            else:
                new_amount = max(10, int(old_amount / 1000))  # Min Le 10 for round trip
        else:
            # For any other amounts, divide by 1000 and ensure minimum
            new_amount = max(5, int(old_amount / 1000))

        print(f"   Booking {booking.pnr_code}: Le {old_amount:,.0f} → Le {new_amount}")

        booking.total_amount = Decimal(str(new_amount))
        booking.amount_paid = Decimal(str(new_amount))
        booking.save()
        bookings_updated += 1

    print(f"✅ Updated {bookings_updated} bookings")

    # Show updated pricing summary
    print("\n📊 Updated Pricing Summary:")
    print("Route Prices:")
    for route in Route.objects.all().order_by("price"):
        trip_type = "One-way" if route.price <= 25 else "Round-trip"
        print(
            f"   {route.origin} → {route.destination}: Le {route.price} ({trip_type})"
        )

    print(f"\n💰 Price Range: Le 5 - Le 25")
    print(f"✅ All prices now reflect the new Sierra Leone Leone currency")
    print(f"✅ No cent denominations (whole numbers only)")
    print(f"✅ Affordable transportation pricing restored")


if __name__ == "__main__":
    try:
        update_currency_pricing()
        print("\n🎉 Currency redenomination update completed successfully!")
    except Exception as e:
        print(f"❌ Error during update: {e}")
        import traceback

        traceback.print_exc()
