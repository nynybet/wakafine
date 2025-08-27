from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.http import JsonResponse, HttpResponse, Http404
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.platypus import Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics import renderPDF
import io
import qrcode
import base64
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import SolidFillColorMask
from PIL import Image
from .models import Booking
from .forms import BookingForm, BookingSearchForm
from sierra_leone_validator import SierraLeoneMobileValidator


class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = "bookings/list.html"
    context_object_name = "bookings"

    def get_queryset(self):
        if self.request.user.is_customer:
            return Booking.objects.filter(customer=self.request.user).order_by(
                "-created_at"
            )
        return Booking.objects.all().order_by("-created_at")


class BookingCreateView(LoginRequiredMixin, CreateView):
    model = Booking
    form_class = BookingForm
    template_name = "bookings/create.html"

    def get_initial(self):
        initial = super().get_initial()
        initial["route"] = self.request.GET.get("route")
        initial["bus"] = self.request.GET.get("bus")
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bus_id = self.request.GET.get("bus")
        route_id = self.request.GET.get("route")
        travel_date = self.request.GET.get("date", timezone.now().date())

        print(f"DEBUG: bus_id={bus_id}, route_id={route_id}, travel_date={travel_date}")

        if bus_id:
            from buses.models import Bus
            from routes.models import Route
            import json

            try:
                bus = Bus.objects.get(id=bus_id)
                context["bus"] = bus
                print(f"DEBUG: Found bus: {bus}")

                if route_id:
                    route = Route.objects.get(id=route_id)
                    context["route"] = route
                    print(f"DEBUG: Found route: {route}")

                # Handle travel_date conversion
                if isinstance(travel_date, str):
                    try:
                        travel_date = timezone.datetime.strptime(
                            travel_date, "%Y-%m-%d"
                        ).date()
                    except ValueError:
                        travel_date = (
                            timezone.now().date()
                        )  # Get seats and their availability
                seats = bus.seats.all().order_by("seat_number")
                print(f"DEBUG: Found {seats.count()} seats for bus")

                booked_seats = Booking.objects.filter(
                    bus=bus,
                    travel_date__date=travel_date,
                    status__in=["confirmed", "pending"],
                ).values_list("seat_id", flat=True)

                print(
                    f"DEBUG: Found {len(booked_seats)} booked seats for date {travel_date}"
                )

                seat_data = []
                for seat in seats:
                    seat_data.append(
                        {
                            "id": seat.id,
                            "number": seat.seat_number,
                            "is_window": seat.is_window,
                            "is_available": seat.is_available
                            and seat.id not in booked_seats,
                            "is_booked": seat.id in booked_seats,
                        }
                    )

                import json

                context["seats"] = seat_data
                context["seats_json"] = json.dumps(seat_data)
                # Verify the JSON is valid
                try:
                    test_parse = json.loads(context["seats_json"])
                    print(f"DEBUG: Valid JSON with {len(test_parse)} seats")
                except json.JSONDecodeError as e:
                    print(f"DEBUG: Invalid JSON: {e}")

                context["travel_date"] = travel_date
                print(f"DEBUG: Added {len(seat_data)} seats to context")
                print(f"DEBUG: seats_json length: {len(context['seats_json'])}")

            except (Bus.DoesNotExist, Route.DoesNotExist) as e:
                print(f"DEBUG: Exception occurred: {e}")
                pass
        else:
            print("DEBUG: No bus_id provided")

        return context

    def form_valid(self, form):
        form.instance.customer = self.request.user

        # Calculate amount based on trip type and route price
        route_price = form.instance.route.price
        trip_type = form.cleaned_data.get("trip_type", "one_way")

        if trip_type == "round_trip":
            form.instance.amount_paid = route_price * 2  # Double price for round trip
            # Ensure return fields are set
            form.instance.return_bus = form.cleaned_data.get("return_bus")
            form.instance.return_seat = form.cleaned_data.get("return_seat")
            form.instance.return_date = form.cleaned_data.get("return_date")
        else:
            form.instance.amount_paid = route_price

        # Convert travel_date (date) to datetime using route departure time
        travel_date = form.cleaned_data["travel_date"]
        departure_time = form.instance.route.departure_time

        # Combine date and time
        form.instance.travel_date = timezone.datetime.combine(
            travel_date, departure_time
        )

        # Make it timezone aware
        if timezone.is_naive(form.instance.travel_date):
            form.instance.travel_date = timezone.make_aware(form.instance.travel_date)

        # Handle return date for round trips
        return_date = form.cleaned_data.get("return_date")
        if trip_type == "round_trip" and return_date:
            form.instance.return_date = timezone.datetime.combine(
                return_date, departure_time
            )
            if timezone.is_naive(form.instance.return_date):
                form.instance.return_date = timezone.make_aware(
                    form.instance.return_date
                )

        booking = form.save()

        # Success message based on trip type
        if trip_type == "round_trip":
            return_seat_info = (
                f" (Return: {booking.return_bus} - Seat {booking.return_seat.seat_number})"
                if booking.return_seat
                else ""
            )
            trip_info = f"round trip (return on {return_date.strftime('%B %d, %Y')}){return_seat_info}"
        else:
            trip_info = "one way trip"

        messages.success(
            self.request,
            f"Booking created successfully! Your PNR is: {booking.pnr_code} for {trip_info}. Outbound seat: {booking.seat.seat_number}{' | Return seat: ' + booking.return_seat.seat_number if booking.return_seat else ''}. Total amount: Le {booking.amount_paid}",
        )
        return redirect("bookings:payment", pk=booking.pk)


class BookingDetailView(DetailView):
    model = Booking
    template_name = "bookings/detail.html"
    context_object_name = "booking"


class TicketView(DetailView):
    model = Booking
    template_name = "bookings/ticket.html"
    context_object_name = "booking"


class BookingSearchView(TemplateView):
    template_name = "bookings/search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = BookingSearchForm(self.request.GET or None)
        booking = None

        if form.is_valid():
            pnr_code = form.cleaned_data.get("pnr_code")
            if pnr_code:
                try:
                    booking = Booking.objects.get(pnr_code=pnr_code)
                except Booking.DoesNotExist:
                    messages.error(self.request, "No booking found with this PNR code.")

        context["form"] = form
        context["booking"] = booking
        return context


class PaymentView(LoginRequiredMixin, TemplateView):
    template_name = "bookings/payment.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # The dispatch method already ensures the booking exists and belongs to the user
        try:
            booking = Booking.objects.get(pk=kwargs["pk"], customer=self.request.user)
            context["booking"] = booking
        except Booking.DoesNotExist:
            # This should rarely happen due to dispatch method, but handle it gracefully
            raise Http404("Booking not found or access denied")
        return context

    def dispatch(self, request, *args, **kwargs):
        # Check if booking exists and belongs to user before processing
        booking_id = kwargs.get("pk")
        try:
            booking = Booking.objects.get(pk=booking_id)
            if booking.customer != request.user:
                messages.error(
                    request,
                    f"Access denied. Booking {booking_id} belongs to {booking.customer.username if booking.customer else 'another user'}.",
                )
                return redirect("bookings:list")
        except Booking.DoesNotExist:
            messages.error(
                request,
                f"Booking {booking_id} not found. Please check your booking ID and try again.",
            )
            return redirect("bookings:list")

        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        booking = get_object_or_404(Booking, pk=kwargs["pk"], customer=request.user)
        payment_method = request.POST.get("payment_method")
        mobile_money_number = request.POST.get("mobile_money_number", "").strip()

        if payment_method:  # Validate mobile money number for mobile money payments
            mobile_money_methods = ["afrimoney", "qmoney", "orange_money"]

            if payment_method in mobile_money_methods:
                if not mobile_money_number:
                    messages.error(
                        request,
                        f"Mobile money number is required for {payment_method.replace('_', ' ').title()} payments.",
                    )
                    return redirect("bookings:payment", pk=booking.pk)

                # Validate mobile money number using new validator
                error_message = (
                    SierraLeoneMobileValidator.validate_payment_compatibility(
                        payment_method, mobile_money_number
                    )
                )
                if error_message:
                    messages.error(request, error_message)
                    return redirect("bookings:payment", pk=booking.pk)

                # Normalize the number using new validator
                normalized_number = SierraLeoneMobileValidator.normalize_number(
                    mobile_money_number
                )
                if not normalized_number:
                    messages.error(
                        request, "Please enter a valid Sierra Leone mobile number."
                    )
                    return redirect("bookings:payment", pk=booking.pk)

                booking.mobile_money_number = normalized_number
                payment_display = payment_method.replace("_", " ").title()

                # Get trip type information for enhanced messaging
                trip_info = ""
                if booking.trip_type == "round_trip" and booking.return_date:
                    trip_info = f" (Round trip - return on {booking.return_date.strftime('%B %d, %Y')})"
                else:
                    trip_info = " (One way trip)"

                success_message = f"Payment successful via {payment_display}! Your booking is confirmed{trip_info}. Payment will be processed to {normalized_number}."

            elif payment_method == "paypal":
                # Get PayPal form data
                card_number = request.POST.get("card_number", "").strip()
                card_owner_name = request.POST.get("card_owner_name", "").strip()
                card_cvc = request.POST.get("card_cvc", "").strip()
                card_expiry = request.POST.get("card_expiry", "").strip()

                # Validate PayPal fields
                validation_errors = self.validate_paypal_fields(
                    card_number, card_owner_name, card_cvc, card_expiry
                )

                if validation_errors:
                    for error in validation_errors:
                        messages.error(request, error)
                    return redirect("bookings:payment", pk=booking.pk)

                # Store PayPal card data
                booking.mobile_money_number = ""  # Clear mobile money number for PayPal
                booking.card_number = card_number
                booking.card_owner_name = card_owner_name
                booking.card_cvc = card_cvc
                booking.card_expiry = card_expiry

                payment_display = "PayPal"

                # Get trip type information for enhanced messaging
                trip_info = ""
                if booking.trip_type == "round_trip" and booking.return_date:
                    trip_info = f" (Round trip - return on {booking.return_date.strftime('%B %d, %Y')})"
                else:
                    trip_info = " (One way trip)"

                success_message = f"Payment successful via {payment_display}! Your booking is confirmed{trip_info}. PayPal transaction ID: PP-{booking.pnr_code}-{timezone.now().strftime('%Y%m%d')}. You will receive a PayPal receipt at your registered email."

            else:
                messages.error(request, "Invalid payment method selected.")
                return redirect(
                    "bookings:payment", pk=booking.pk
                )  # Process payment (simulation)            booking.payment_method = payment_method
            booking.status = "confirmed"
            booking.save()

            messages.success(request, success_message)
            return redirect("bookings:payment_success", pk=booking.pk)

        messages.error(request, "Please select a payment method.")
        return redirect("bookings:payment", pk=booking.pk)

    def validate_paypal_fields(
        self, card_number, card_owner_name, card_cvc, card_expiry
    ):
        """Validate PayPal card fields"""
        import re

        errors = []

        # Validate card number
        if not card_number:
            errors.append("Card number is required for PayPal payments.")
        else:
            # Remove spaces and validate card number using Luhn algorithm
            clean_number = re.sub(r"\s", "", card_number)
            if not re.match(r"^\d{13,19}$", clean_number):
                errors.append("Card number must be 13-19 digits.")
            elif not self.luhn_check(clean_number):
                errors.append("Please enter a valid card number.")

        # Validate cardholder name
        if not card_owner_name:
            errors.append("Cardholder name is required for PayPal payments.")
        elif len(card_owner_name) < 2:
            errors.append("Please enter the full cardholder name.")

        # Validate CVC
        if not card_cvc:
            errors.append("CVC is required for PayPal payments.")
        elif not re.match(r"^\d{3,4}$", card_cvc):
            errors.append("CVC must be 3-4 digits.")

        # Validate expiry date
        if not card_expiry:
            errors.append("Expiry date is required for PayPal payments.")
        elif not re.match(r"^\d{2}/\d{2}$", card_expiry):
            errors.append("Expiry date must be in MM/YY format.")
        else:
            # Check if expiry date is not in the past
            try:
                month, year = map(int, card_expiry.split("/"))
                if month < 1 or month > 12:
                    errors.append("Invalid expiry month (must be 01-12).")
                else:
                    from datetime import datetime

                    current_date = datetime.now()
                    current_year = current_date.year % 100
                    current_month = current_date.month

                    if year < current_year or (
                        year == current_year and month < current_month
                    ):
                        errors.append("Card has expired. Please use a valid card.")
            except ValueError:
                errors.append("Invalid expiry date format.")

        return errors

    def luhn_check(self, card_number):
        """Validate card number using Luhn algorithm"""

        def digits_of(n):
            return [int(d) for d in str(n)]

        digits = digits_of(card_number)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d * 2))
        return checksum % 10 == 0


class PaymentSuccessView(LoginRequiredMixin, DetailView):
    model = Booking
    template_name = "bookings/payment_success.html"
    context_object_name = "booking"

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_admin:
            return Booking.objects.all()
        return Booking.objects.filter(customer=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking = self.get_object()

        # --- Server-Side QR Code Generation with Round Trip Support ---
        passenger_name = booking.customer.get_full_name() or booking.customer.username
        qr_data_lines = [
            "WAKA-FINE TICKET",
            f"PNR: {booking.pnr_code}",
            f"Passenger: {passenger_name}",
            f"Route: {booking.route.origin} to {booking.route.destination}",
            f"Date: {booking.travel_date.strftime('%b %d, %Y at %H:%M')}",
            f"Bus: {booking.bus.bus_name}",
            f"Seat: {booking.seat.seat_number}",
        ]

        # Add trip type and return trip details if available
        if booking.trip_type == "round_trip":
            qr_data_lines.append("Trip Type: Round Trip")

            # Add return trip details when they exist
            if booking.return_date:
                qr_data_lines.append(
                    f"Return Date: {booking.return_date.strftime('%b %d, %Y at %H:%M')}"
                )
            if booking.return_bus:
                qr_data_lines.append(f"Return Bus: {booking.return_bus.bus_name}")
            if booking.return_seat:
                qr_data_lines.append(f"Return Seat: {booking.return_seat.seat_number}")
        else:
            qr_data_lines.append("Trip Type: One Way")

        # Add payment and status info
        qr_data_lines.extend(
            [
                f"Amount: Le {booking.amount_paid}",
                f"Payment: {booking.get_payment_method_display()}",
                f"Status: {booking.get_status_display()}",
                "",
                f"Ticket URL: {self.request.build_absolute_uri(reverse('bookings:ticket', kwargs={'pk': booking.pk}))}",
            ]
        )

        # Generate QR code
        qr_data_string = "\n".join(qr_data_lines)

        try:
            # Generate QR code image
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=6,
                border=2,
            )
            qr.add_data(qr_data_string)
            qr.make(fit=True)

            # Create an image from the QR Code instance with blue color
            img = qr.make_image(fill_color="#2563eb", back_color="white")

            # Save QR code to a bytes buffer
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")

            # Encode the image in base64 and add to context
            qr_code_image = base64.b64encode(buffer.getvalue()).decode("utf-8")
            context["qr_code_image"] = qr_code_image
            context["qr_data"] = qr_data_string  # For debugging

        except Exception as e:
            print(f"PaymentSuccess QR Code generation error: {e}")
            context["qr_code_error"] = str(e)

        # --- End Server-Side QR Code Generation with Round Trip Support ---

        return context


def get_seat_availability(request):
    """AJAX view to get seat availability for a specific bus and date."""
    if request.method == "GET":
        bus_id = request.GET.get("bus_id")
        travel_date = request.GET.get("travel_date")

        if not bus_id or not travel_date:
            return JsonResponse({"error": "Missing bus_id or travel_date"}, status=400)

        try:
            from buses.models import Bus

            bus = Bus.objects.get(id=bus_id)

            # Parse travel date
            try:
                travel_date = timezone.datetime.strptime(travel_date, "%Y-%m-%d").date()
            except ValueError:
                return JsonResponse({"error": "Invalid date format"}, status=400)

            # Get all seats for the bus
            seats = bus.seats.all().order_by("seat_number")

            # Get booked seats for this date
            booked_seats = Booking.objects.filter(
                bus=bus,
                travel_date__date=travel_date,
                status__in=["confirmed", "pending"],
            ).values_list(
                "seat_id", flat=True
            )  # Prepare seat data
            seat_data = []
            for seat in seats:
                seat_data.append(
                    {
                        "id": seat.id,
                        "number": seat.seat_number,
                        "is_window": seat.is_window,
                        "is_available": seat.is_available
                        and seat.id not in booked_seats,
                        "is_booked": seat.id in booked_seats,
                    }
                )

            return JsonResponse(
                {
                    "seats": seat_data,
                    "bus_name": bus.bus_name,
                    "total_seats": len(seat_data),
                    "available_seats": len([s for s in seat_data if s["is_available"]]),
                }
            )

        except Bus.DoesNotExist:
            return JsonResponse({"error": "Bus not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Method not allowed"}, status=405)


class TicketPDFView(LoginRequiredMixin, DetailView):
    """Generate and download ticket as PDF with modern design matching the web ticket"""

    model = Booking

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_admin:
            return Booking.objects.all()
        return Booking.objects.filter(customer=self.request.user)

    def get(self, request, *args, **kwargs):
        booking = self.get_object()

        # Create PDF in memory
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # Colors matching the web design
        green_color = HexColor("#10b981")  # Green header
        blue_color = HexColor("#3b82f6")  # Blue footer
        gray_bg = HexColor("#f9fafb")  # Gray background
        dark_text = HexColor("#1f2937")  # Dark text
        medium_text = HexColor("#6b7280")  # Medium text

        # Start y position for content
        y_pos = height - 60

        # Header with green background
        p.setFillColor(green_color)
        p.rect(40, y_pos - 40, width - 80, 60, fill=1, stroke=0)

        # Header text
        p.setFillColor(colors.white)
        p.setFont("Helvetica-Bold", 18)
        p.drawString(60, y_pos - 15, "Digital Ticket")
        p.setFont("Helvetica", 12)
        p.drawString(60, y_pos - 30, "Waka-Fine Bus")

        # PNR Code in header (right side)
        p.setFont("Helvetica", 10)
        p.drawString(width - 160, y_pos - 15, "PNR")
        p.setFont("Helvetica-Bold", 14)
        p.drawString(width - 160, y_pos - 30, booking.pnr_code)

        y_pos -= 80

        # Route section with visual line and bus icon
        p.setFillColor(dark_text)
        p.setFont("Helvetica-Bold", 16)

        # Origin
        p.drawString(80, y_pos, booking.route.origin)
        p.setFont("Helvetica", 10)
        p.drawString(80, y_pos - 15, booking.route.departure_time.strftime("%H:%M"))

        # Destination
        p.setFont("Helvetica-Bold", 16)
        p.drawString(width - 180, y_pos, booking.route.destination)
        p.setFont("Helvetica", 10)
        p.drawString(
            width - 180, y_pos - 15, booking.route.arrival_time.strftime("%H:%M")
        )

        # Dashed line between origin and destination
        p.setDash(3, 3)
        p.setStrokeColor(medium_text)
        p.line(160, y_pos - 5, width - 240, y_pos - 5)
        p.setDash()  # Reset to solid

        # Bus icon representation (simple text)
        p.setFont("Helvetica", 14)
        p.drawCentredText((width) / 2, y_pos - 5, "🚌")

        y_pos -= 50

        # Travel details in grid format
        details_y = y_pos
        box_width = (width - 120) / 2
        box_height = 30

        # Date box
        p.setFillColor(gray_bg)
        p.rect(60, details_y - box_height, box_width - 10, box_height, fill=1, stroke=0)
        p.setFillColor(medium_text)
        p.setFont("Helvetica", 8)
        p.drawString(70, details_y - 10, "DATE")
        p.setFillColor(dark_text)
        p.setFont("Helvetica-Bold", 10)
        p.drawString(70, details_y - 22, booking.travel_date.strftime("%b %d, %Y"))

        # Bus box
        p.setFillColor(gray_bg)
        p.rect(
            60 + box_width,
            details_y - box_height,
            box_width - 10,
            box_height,
            fill=1,
            stroke=0,
        )
        p.setFillColor(medium_text)
        p.setFont("Helvetica", 8)
        p.drawString(70 + box_width, details_y - 10, "BUS")
        p.setFillColor(dark_text)
        p.setFont("Helvetica-Bold", 10)
        p.drawString(70 + box_width, details_y - 22, booking.bus.bus_name)

        details_y -= 40

        # Seat box
        p.setFillColor(gray_bg)
        p.rect(60, details_y - box_height, box_width - 10, box_height, fill=1, stroke=0)
        p.setFillColor(medium_text)
        p.setFont("Helvetica", 8)
        p.drawString(70, details_y - 10, "SEAT")
        p.setFillColor(blue_color)
        p.setFont("Helvetica-Bold", 10)
        p.drawString(
            70,
            details_y - 22,
            booking.seat.seat_number if booking.seat else "Not assigned",
        )

        # Amount box
        p.setFillColor(gray_bg)
        p.rect(
            60 + box_width,
            details_y - box_height,
            box_width - 10,
            box_height,
            fill=1,
            stroke=0,
        )
        p.setFillColor(medium_text)
        p.setFont("Helvetica", 8)
        p.drawString(70 + box_width, details_y - 10, "AMOUNT")
        p.setFillColor(dark_text)
        p.setFont("Helvetica-Bold", 10)
        p.drawString(70 + box_width, details_y - 22, f"Le {booking.amount_paid:.0f}")

        y_pos = details_y - 60

        # Passenger Information section
        p.setStrokeColor(colors.lightgrey)
        p.line(60, y_pos, width - 60, y_pos)
        y_pos -= 20

        p.setFillColor(medium_text)
        p.setFont("Helvetica", 8)
        p.drawString(60, y_pos, "PASSENGER")
        y_pos -= 15

        p.setFillColor(dark_text)
        p.setFont("Helvetica-Bold", 12)
        passenger_name = booking.customer.get_full_name() or booking.customer.username
        p.drawString(60, y_pos, passenger_name)
        y_pos -= 15

        p.setFillColor(medium_text)
        p.setFont("Helvetica", 10)
        p.drawString(60, y_pos, booking.customer.email)

        y_pos -= 40

        # Payment Information section
        p.setStrokeColor(colors.lightgrey)
        p.line(60, y_pos, width - 60, y_pos)
        y_pos -= 20

        p.setFillColor(medium_text)
        p.setFont("Helvetica", 8)
        p.drawString(60, y_pos, "PAYMENT DETAILS")
        y_pos -= 15

        p.setFillColor(dark_text)
        p.setFont("Helvetica", 10)
        p.drawString(60, y_pos, f"Method: {booking.get_payment_method_display()}")

        if booking.mobile_money_number:
            y_pos -= 15
            p.drawString(60, y_pos, f"Mobile Number: {booking.mobile_money_number}")

        y_pos -= 15
        p.setFillColor(blue_color)
        p.setFont("Helvetica-Bold", 10)
        p.drawString(60, y_pos, f"Amount: Le {booking.amount_paid:.0f}")

        y_pos -= 40

        # QR Code section
        p.setStrokeColor(colors.lightgrey)
        p.line(60, y_pos, width - 60, y_pos)
        y_pos -= 20

        # Generate QR code
        qr_data = f"""WAKA-FINE BUS TICKET
PNR: {booking.pnr_code}
Passenger: {passenger_name}
Route: {booking.route.origin} to {booking.route.destination}
Date: {booking.travel_date.strftime('%b %d, %Y %H:%M')}
Bus: {booking.bus.bus_name}
Seat: {booking.seat.seat_number if booking.seat else 'Not assigned'}
Amount: Le {booking.amount_paid:.0f}"""

        try:
            # Create QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=3,
                border=2,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)

            # Create QR code image with blue color
            blue_rgb = (
                int(blue_color.red * 255),
                int(blue_color.green * 255),
                int(blue_color.blue * 255),
            )
            qr_img = qr.make_image(
                image_factory=StyledPilImage,
                color_mask=SolidFillColorMask(front_color=blue_rgb),
            )

            # Save QR code to buffer
            qr_buffer = io.BytesIO()
            qr_img.save(qr_buffer, format="PNG")
            qr_buffer.seek(0)

            # Draw QR code on PDF (centered)
            qr_size = 80
            qr_x = (width - qr_size) / 2
            p.drawInlineImage(qr_buffer, qr_x, y_pos - qr_size - 20, qr_size, qr_size)

            # QR code label
            p.setFillColor(medium_text)
            p.setFont("Helvetica", 8)
            p.drawCentredText(
                width / 2, y_pos - qr_size - 35, "Scan QR code for verification"
            )

        except Exception as e:
            # Fallback text if QR code generation fails
            p.setFillColor(gray_bg)
            p.rect((width - 80) / 2, y_pos - 100, 80, 80, fill=1, stroke=1)
            p.setFillColor(medium_text)
            p.setFont("Helvetica", 8)
            p.drawCentredText(width / 2, y_pos - 55, "QR Code")
            p.drawCentredText(width / 2, y_pos - 65, booking.pnr_code)

        y_pos -= 140

        # Footer with blue background
        footer_height = 40
        p.setFillColor(blue_color)
        p.rect(40, y_pos - footer_height, width - 80, footer_height, fill=1, stroke=0)

        p.setFillColor(colors.white)
        p.setFont("Helvetica", 8)
        footer_text = "Please present this ticket at the boarding point. Keep your ID ready for verification."
        p.drawCentredText(width / 2, y_pos - 15, footer_text)

        support_text = f"Support: +232 785 45477 | Generated: {timezone.now().strftime('%d/%m/%Y %H:%M')}"
        p.drawCentredText(width / 2, y_pos - 28, support_text)

        # Finalize PDF
        p.showPage()
        p.save()

        # Return PDF response
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="ticket_{booking.pnr_code}.pdf"'
        )

        return response


# Unified TicketView for all users and print
class TicketView(DetailView):
    """Unified ticket view for all users and print, always uses the same template and layout."""

    model = Booking
    template_name = "bookings/ticket_print.html"
    context_object_name = "booking"

    def get_queryset(self):
        # Allow access to any booking for now (for testing)
        # TODO: Add proper authentication checks in production
        if self.request.user.is_authenticated and (
            self.request.user.is_staff or self.request.user.is_admin
        ):
            return Booking.objects.all()
        elif self.request.user.is_authenticated:
            return Booking.objects.filter(customer=self.request.user)
        # For public/unauthenticated, restrict or allow as needed
        return Booking.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking = self.get_object()

        # --- Server-Side QR Code Generation with Round Trip Support ---
        passenger_name = booking.customer.get_full_name() or booking.customer.username
        qr_data_string = f"""WAKA-FINE TICKET
PNR: {booking.pnr_code}
Passenger: {passenger_name}
Route: {booking.route.origin} to {booking.route.destination}
Date: {booking.travel_date.strftime('%b %d, %Y at %H:%M')}
Bus: {booking.bus.bus_name}
Seat: {booking.seat.seat_number}"""

        # Add round trip information if it exists
        if booking.trip_type == "round_trip":
            qr_data_string += f"\nTrip Type: Round Trip"

            if booking.return_date:
                qr_data_string += f"\nReturn Date: {booking.return_date.strftime('%b %d, %Y at %H:%M')}"
            if booking.return_bus:
                qr_data_string += f"\nReturn Bus: {booking.return_bus.bus_name}"
            if booking.return_seat:
                qr_data_string += f"\nReturn Seat: {booking.return_seat.seat_number}"
        else:
            qr_data_string += f"\nTrip Type: One Way"

        qr_data_string += f"""
Amount: Le {booking.amount_paid}
Status: {booking.get_status_display()}"""

        # Generate QR code image
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data_string)
        qr.make(fit=True)

        # Create an image from the QR Code instance
        img = qr.make_image(
            fill_color="#1e3a8a", back_color="white"  # Professional blue
        )

        # Save QR code to a bytes buffer
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")

        # Encode the image in base64 and add to context
        qr_code_image = base64.b64encode(buffer.getvalue()).decode("utf-8")
        context["qr_code_image"] = qr_code_image
        # --- End Server-Side QR Code Generation with Round Trip Support ---

        # Show print button and nav only if not in print mode
        context["print_view"] = self.request.GET.get(
            "print", "false"
        ).lower() == "true" or self.request.path.endswith("/print/")
        context["autoprint"] = (
            self.request.GET.get("autoprint", "false").lower() == "true"
        )
        context["show_nav"] = not context["print_view"]
        return context


def get_route_buses_ajax(request):
    """AJAX view to get buses for a specific route."""
    if request.method == "GET":
        route_id = request.GET.get("route_id")

        if not route_id:
            return JsonResponse({"error": "Missing route_id"}, status=400)

        try:
            from routes.models import Route
            from buses.models import Bus

            route = Route.objects.get(id=route_id)
            buses = Bus.objects.filter(assigned_route=route, is_active=True)

            bus_data = []
            for bus in buses:
                bus_data.append(
                    {
                        "id": bus.id,
                        "name": bus.bus_name,
                        "number": bus.bus_number,
                        "capacity": bus.seats.count() if hasattr(bus, "seats") else 0,
                    }
                )

            return JsonResponse(
                {
                    "buses": bus_data,
                    "route_name": f"{route.origin} → {route.destination}",
                    "route_price": float(route.price),
                    "departure_time": route.departure_time.strftime("%H:%M"),
                    "arrival_time": route.arrival_time.strftime("%H:%M"),
                }
            )

        except Route.DoesNotExist:
            return JsonResponse({"error": "Route not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Method not allowed"}, status=405)


class BookingDebugView(TemplateView):
    template_name = "bookings/debug.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bus_id = self.request.GET.get("bus")
        route_id = self.request.GET.get("route")
        travel_date = self.request.GET.get("date", timezone.now().date())

        print(f"DEBUG: bus_id={bus_id}, route_id={route_id}, travel_date={travel_date}")

        if bus_id:
            from buses.models import Bus
            from routes.models import Route
            import json

            try:
                bus = Bus.objects.get(id=bus_id)
                context["bus"] = bus
                print(f"DEBUG: Found bus: {bus}")

                if route_id:
                    route = Route.objects.get(id=route_id)
                    context["route"] = route
                    print(f"DEBUG: Found route: {route}")

                # Handle travel_date conversion
                if isinstance(travel_date, str):
                    try:
                        travel_date = timezone.datetime.strptime(
                            travel_date, "%Y-%m-%d"
                        ).date()
                    except ValueError:
                        travel_date = timezone.now().date()

                # Get seats and their availability
                seats = bus.seats.all().order_by("seat_number")
                print(f"DEBUG: Found {seats.count()} seats for bus")

                booked_seats = Booking.objects.filter(
                    bus=bus,
                    travel_date__date=travel_date,
                    status__in=["confirmed", "pending"],
                ).values_list("seat_id", flat=True)

                print(
                    f"DEBUG: Found {len(booked_seats)} booked seats for date {travel_date}"
                )

                seat_data = []
                for seat in seats:
                    seat_data.append(
                        {
                            "id": seat.id,
                            "number": seat.seat_number,
                            "is_window": seat.is_window,
                            "is_available": seat.is_available
                            and seat.id not in booked_seats,
                            "is_booked": seat.id in booked_seats,
                        }
                    )

                context["seats"] = seat_data
                context["seats_json"] = json.dumps(seat_data)
                context["travel_date"] = travel_date
                print(f"DEBUG: Added {len(seat_data)} seats to context")
                print(f"DEBUG: seats_json length: {len(context['seats_json'])}")

            except (Bus.DoesNotExist, Route.DoesNotExist) as e:
                print(f"DEBUG: Exception occurred: {e}")
                pass
        else:
            print("DEBUG: No bus_id provided")

        return context
