#!/usr/bin/env python3
"""
Direct database update for currency redenomination
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine_bus.settings")
django.setup()

from django.db import connection


def update_pricing_sql():
    """Update pricing using direct SQL commands"""
    print("=== Direct SQL Currency Update ===")

    with connection.cursor() as cursor:
        # First, show current route prices
        print("Current route prices:")
        cursor.execute(
            "SELECT id, name, origin, destination, price FROM routes_route LIMIT 10"
        )
        for row in cursor.fetchall():
            print(f"  Route {row[0]}: {row[1]} - Le {row[4]}")

        # Update route prices (divide by 1000, minimum 5)
        print("\nUpdating route prices...")
        cursor.execute(
            """
            UPDATE routes_route 
            SET price = CASE 
                WHEN CAST(price AS INTEGER) / 1000 < 5 THEN 5
                ELSE CAST(price AS INTEGER) / 1000
            END
        """
        )

        routes_updated = cursor.rowcount
        print(f"Updated {routes_updated} routes")

        # Show updated route prices
        print("\nUpdated route prices:")
        cursor.execute(
            "SELECT id, name, origin, destination, price FROM routes_route LIMIT 10"
        )
        for row in cursor.fetchall():
            print(f"  Route {row[0]}: {row[1]} - Le {row[4]}")

        # Update booking amounts
        print("\nUpdating booking amounts...")
        cursor.execute(
            """
            UPDATE bookings_booking 
            SET total_amount = CASE 
                WHEN CAST(total_amount AS INTEGER) / 1000 < 5 THEN 5
                ELSE CAST(total_amount AS INTEGER) / 1000
            END,
            amount_paid = CASE 
                WHEN CAST(amount_paid AS INTEGER) / 1000 < 5 THEN 5
                ELSE CAST(amount_paid AS INTEGER) / 1000
            END
        """
        )

        bookings_updated = cursor.rowcount
        print(f"Updated {bookings_updated} bookings")

        # Show price summary
        print("\nPrice summary:")
        cursor.execute("SELECT MIN(price), MAX(price), COUNT(*) FROM routes_route")
        min_price, max_price, count = cursor.fetchone()
        print(f"  {count} routes with prices from Le {min_price} to Le {max_price}")

        print("\n✅ Currency redenomination completed via SQL!")


if __name__ == "__main__":
    try:
        update_pricing_sql()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
