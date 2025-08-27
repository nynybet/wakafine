from django.core.management.base import BaseCommand
from routes.models import Route
from bookings.models import Booking
from decimal import Decimal


class Command(BaseCommand):
    help = "Update currency pricing from thousands to tens due to Sierra Leone redenomination"

    def handle(self, *args, **options):
        self.stdout.write("=== Sierra Leone Currency Redenomination ===")
        self.stdout.write("Converting thousands to tens (e.g., Le 15,000 → Le 15)")

        # Update Routes
        self.stdout.write("\n🚌 Updating Routes...")
        routes = Route.objects.all()
        routes_updated = 0

        for route in routes:
            old_price = float(route.price)
            # Convert thousands to tens, minimum Le 5, maximum Le 25
            new_price = max(5, min(25, round(old_price / 1000)))

            self.stdout.write(
                f"   {route.origin} → {route.destination}: Le {old_price:,.0f} → Le {new_price}"
            )

            route.price = Decimal(str(new_price))
            route.save()
            routes_updated += 1

        self.stdout.write(f"✅ Updated {routes_updated} routes")

        # Update Bookings
        self.stdout.write("\n🎫 Updating Bookings...")
        bookings = Booking.objects.all()
        bookings_updated = 0

        for booking in bookings:
            old_amount = float(booking.amount_paid)
            # Convert thousands to tens
            new_amount = max(5, round(old_amount / 1000))

            self.stdout.write(
                f"   Booking {booking.pnr_code}: Le {old_amount:,.0f} → Le {new_amount}"
            )

            booking.amount_paid = Decimal(str(new_amount))
            booking.save()
            bookings_updated += 1

        self.stdout.write(f"✅ Updated {bookings_updated} bookings")

        # Summary
        self.stdout.write("\n📊 New Pricing Summary:")
        prices = [float(route.price) for route in Route.objects.all()]
        if prices:
            min_price = min(prices)
            max_price = max(prices)
            unique_prices = sorted(set(prices))

            self.stdout.write(
                f"   Price Range: Le {min_price:.0f} - Le {max_price:.0f}"
            )
            self.stdout.write(
                f"   Available Fares: {', '.join([f'Le {p:.0f}' for p in unique_prices])}"
            )

        self.stdout.write("\n🎉 Currency redenomination completed!")
        self.stdout.write("   ✅ All prices now in affordable tens (Le 5-25)")
        self.stdout.write("   ✅ No cents used (whole numbers only)")
        self.stdout.write("   ✅ Transportation is now affordable for everyone")
