from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import qrcode
from io import BytesIO
from django.core.files import File
import uuid
import string
import random

User = get_user_model()


class Booking(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ("afrimoney", "Afrimoney"),
        ("qmoney", "Qmoney"),
        ("orange_money", "Orange Money"),
        ("paypal", "PayPal"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    ]

    # Booking Details
    pnr_code = models.CharField(max_length=10, unique=True, editable=False)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    route = models.ForeignKey("routes.Route", on_delete=models.CASCADE)
    bus = models.ForeignKey("buses.Bus", on_delete=models.CASCADE)
    seat = models.ForeignKey("buses.Seat", on_delete=models.CASCADE)

    # Travel Details
    travel_date = models.DateTimeField()
    booking_date = models.DateTimeField(auto_now_add=True)

    # Payment Details
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    # QR Code
    qr_code = models.ImageField(upload_to="qr_codes/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["bus", "seat", "travel_date"]

    def save(self, *args, **kwargs):
        if not self.pnr_code:
            self.pnr_code = self.generate_pnr()
        super().save(*args, **kwargs)
        if not self.qr_code:
            self.generate_qr_code()

    def generate_pnr(self):
        """Generate a unique PNR code"""
        while True:
            pnr = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
            if not Booking.objects.filter(pnr_code=pnr).exists():
                return pnr

    def generate_qr_code(self):
        """Generate QR code for the booking with destination and terminal info"""
        # Get terminal information
        origin_terminal = (
            self.route.origin_terminal.name if self.route.origin_terminal else "N/A"
        )
        destination_terminal = (
            self.route.destination_terminal.name
            if self.route.destination_terminal
            else "N/A"
        )

        qr_data = {
            "pnr": self.pnr_code,
            "route": str(self.route),
            "origin_terminal": origin_terminal,
            "destination_terminal": destination_terminal,
            "bus": self.bus.bus_name,
            "seat": self.seat.seat_number,
            "date": self.travel_date.strftime("%Y-%m-%d %H:%M"),
            "passenger": self.customer.get_full_name() or self.customer.username,
            "destination": self.route.get_destination_display(),
        }

        qr_string = (
            f"WAKA-FINE BUS TICKET\\n"
            f"PNR: {qr_data['pnr']}\\n"
            f"Route: {qr_data['route']}\\n"
            f"From: {qr_data['origin_terminal']}\\n"
            f"To: {qr_data['destination_terminal']}\\n"
            f"Destination: {qr_data['destination']}\\n"
            f"Bus: {qr_data['bus']}\\n"
            f"Seat: {qr_data['seat']}\\n"
            f"Date: {qr_data['date']}\\n"
            f"Passenger: {qr_data['passenger']}"
        )

        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_string)
        qr.make(fit=True)

        qr_image = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        qr_image.save(buffer, format="PNG")
        buffer.seek(0)

        filename = f"qr_{self.pnr_code}.png"
        self.qr_code.save(filename, File(buffer), save=False)
        self.save()

    def __str__(self):
        return f"PNR: {self.pnr_code} - {self.customer.username}"

    @property
    def is_past_travel_date(self):
        return timezone.now() > self.travel_date
