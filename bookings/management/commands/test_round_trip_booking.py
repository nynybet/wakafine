from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from bookings.models import Booking
from routes.models import Route
from buses.models import Bus, Seat
from datetime import datetime, timedelta

User = get_user_model()


class Command(BaseCommand):
    help = "Test round trip booking functionality"

    def handle(self, *args, **options):
        self.stdout.write("🧪 Testing Round Trip Booking...")

        # Get test data
        user = User.objects.filter(username__icontains="test").first()
        if not user:
            user = User.objects.create_user(
                username="test_roundtrip_user",
                email="test@example.com",
                password="test123",
                first_name="Test",
                last_name="User",
                phone_number="+23276123456",
            )
            self.stdout.write(f"✅ Created test user: {user.username}")

        # Get routes and buses
        route = Route.objects.first()
        if not route:
            self.stdout.write(self.style.ERROR("❌ No routes found"))
            return

        buses = Bus.objects.filter(assigned_route=route)
        if buses.count() < 2:
            self.stdout.write(self.style.ERROR("❌ Need at least 2 buses"))
            return

        bus1, bus2 = buses[0], buses[1]

        # Get seats
        seat1 = Seat.objects.filter(bus=bus1, is_available=True).first()
        seat2 = Seat.objects.filter(bus=bus2, is_available=True).first()

        if not seat1 or not seat2:
            self.stdout.write(self.style.ERROR("❌ No available seats"))
            return

        # Create round trip booking
        tomorrow = datetime.now().date() + timedelta(days=1)
        day_after = tomorrow + timedelta(days=1)

        booking = Booking.objects.create(
            customer=user,
            route=route,
            travel_date=datetime.combine(tomorrow, datetime.min.time().replace(hour=9)),
            bus=bus1,
            seat=seat1,
            trip_type="round_trip",
            return_date=datetime.combine(
                day_after, datetime.min.time().replace(hour=15)
            ),
            return_bus=bus2,
            return_seat=seat2,
            amount_paid=route.price * 2,
            payment_method="cash",
            status="confirmed",
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Round trip booking created!\n"
                f"   PNR: {booking.pnr_code}\n"
                f"   Trip Type: {booking.trip_type}\n"
                f"   Is Round Trip: {booking.is_round_trip}\n"
                f"   Outbound: {booking.seat.seat_number}\n"
                f"   Return: {booking.return_seat.seat_number if booking.return_seat else 'None'}\n"
                f"   Amount: Le {booking.amount_paid}"
            )
        )
