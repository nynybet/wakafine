from django.core.management.base import BaseCommand
from buses.models import Bus, Seat


class Command(BaseCommand):
    help = "Generate seats for all buses"

    def handle(self, *args, **options):
        buses = Bus.objects.all()

        for bus in buses:
            if bus.seats.exists():
                self.stdout.write(
                    self.style.WARNING(f"Seats already exist for {bus.bus_name}")
                )
                continue

            self.stdout.write(f"Generating seats for {bus.bus_name}...")

            # Generate seats based on bus type
            if bus.bus_type == "mini":
                self.generate_mini_bus_seats(bus)
            elif bus.bus_type == "standard":
                self.generate_standard_bus_seats(bus)
            elif bus.bus_type == "large":
                self.generate_large_bus_seats(bus)

            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully generated {bus.seat_capacity} seats for {bus.bus_name}"
                )
            )

    def generate_mini_bus_seats(self, bus):
        """Generate seats for mini bus (14 seats)"""
        seat_layout = [
            # Row 1: 1, 2 (driver side), 3, 4
            (1, True),
            (2, False),
            (3, False),
            (4, True),
            # Row 2: 5, 6, 7, 8
            (5, True),
            (6, False),
            (7, False),
            (8, True),
            # Row 3: 9, 10, 11, 12
            (9, True),
            (10, False),
            (11, False),
            (12, True),
            # Row 4: 13, 14 (back row)
            (13, True),
            (14, True),
        ]

        for seat_num, is_window in seat_layout:
            Seat.objects.create(
                bus=bus,
                seat_number=str(seat_num),
                is_window=is_window,
                is_available=True,
            )

    def generate_standard_bus_seats(self, bus):
        """Generate seats for standard bus (25 seats)"""
        seat_layout = []

        # Rows 1-6: 2+2 seating
        for row in range(1, 7):
            base = (row - 1) * 4
            seat_layout.extend(
                [
                    (base + 1, True),  # Window left
                    (base + 2, False),  # Aisle left
                    (base + 3, False),  # Aisle right
                    (base + 4, True),  # Window right
                ]
            )

        # Last row: single seat
        seat_layout.append((25, True))

        for seat_num, is_window in seat_layout:
            Seat.objects.create(
                bus=bus,
                seat_number=str(seat_num),
                is_window=is_window,
                is_available=True,
            )

    def generate_large_bus_seats(self, bus):
        """Generate seats for large bus (35 seats)"""
        seat_layout = []

        # Rows 1-8: 2+2 seating
        for row in range(1, 9):
            base = (row - 1) * 4
            seat_layout.extend(
                [
                    (base + 1, True),  # Window left
                    (base + 2, False),  # Aisle left
                    (base + 3, False),  # Aisle right
                    (base + 4, True),  # Window right
                ]
            )

        # Last row: 3 seats
        seat_layout.extend([(33, True), (34, False), (35, True)])

        for seat_num, is_window in seat_layout:
            Seat.objects.create(
                bus=bus,
                seat_number=str(seat_num),
                is_window=is_window,
                is_available=True,
            )
