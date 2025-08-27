from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from bookings.models import Route, Bus, Seat, Booking
from accounts.models import Terminal
from datetime import datetime, timedelta

User = get_user_model()


class Command(BaseCommand):
    help = "Test round trip booking functionality"

    def handle(self, *args, **options):
        self.stdout.write("🧪 Testing Round Trip Booking...")

        # Create test user
        user, created = User.objects.get_or_create(
            username="testuser_roundtrip",
            defaults={
                "email": "test@example.com",
                "first_name": "Test",
                "last_name": "User",
                "phone_number": "+23276123456",
            },
        )

        if created:
            user.set_password("testpass123")
            user.save()

        # Get existing routes and buses
        routes = Route.objects.all()[:2]
        if len(routes) < 2:
            self.stdout.write(
                self.style.ERROR("Need at least 2 routes for round trip testing")
            )
            return

        route1, route2 = routes[0], routes[1]

        # Get buses for the routes
        bus1 = Bus.objects.filter(route=route1).first()
        bus2 = Bus.objects.filter(route=route2).first()

        if not bus1 or not bus2:
            self.stdout.write(self.style.ERROR("Need buses for both routes"))
            return

        # Get available seats
        seat1 = Seat.objects.filter(bus=bus1, is_available=True).first()
        seat2 = Seat.objects.filter(bus=bus2, is_available=True).first()

        if not seat1 or not seat2:
            self.stdout.write(self.style.ERROR("Need available seats on both buses"))
            return

        # Create a round trip booking
        tomorrow = datetime.now().date() + timedelta(days=1)
        day_after = tomorrow + timedelta(days=1)

        booking = Booking.objects.create(
            customer=user,
            route=route1,
            travel_date=datetime.combine(tomorrow, datetime.min.time().replace(hour=9)),
            bus=bus1,
            seat=seat1,
            is_round_trip=True,
            return_route=route2,
            return_travel_date=datetime.combine(
                day_after, datetime.min.time().replace(hour=15)
            ),
            return_bus=bus2,
            return_seat=seat2,
            amount_paid=route1.base_price * 2,  # Round trip
            payment_method="cash",
            status="confirmed",
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Round trip booking created successfully!\n"
                f"   PNR: {booking.pnr_code}\n"
                f"   Outbound: {route1.origin} → {route1.destination} (Seat {seat1.seat_number})\n"
                f"   Return: {route2.origin} → {route2.destination} (Seat {seat2.seat_number})\n"
                f"   Amount: Le {booking.amount_paid}"
            )
        )

        # Test if both seats are shown
        self.stdout.write("🔍 Checking seat information...")

        if booking.seat:
            self.stdout.write(f"   ✅ Outbound seat: {booking.seat.seat_number}")
        else:
            self.stdout.write("   ❌ No outbound seat")

        if booking.return_seat:
            self.stdout.write(f"   ✅ Return seat: {booking.return_seat.seat_number}")
        else:
            self.stdout.write("   ❌ No return seat")

        self.stdout.write(self.style.SUCCESS("🎉 Round trip booking test completed!"))
