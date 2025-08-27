from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
from .models import Booking
from .forms import BookingForm, BookingSearchForm


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
        if bus_id:
            from buses.models import Bus

            try:
                bus = Bus.objects.get(id=bus_id)
                context["bus"] = bus
                context["seats"] = []
            except Bus.DoesNotExist:
                pass
        return context

    def form_valid(self, form):
        form.instance.customer = self.request.user
        booking = form.save()
        messages.success(
            self.request,
            f"Booking created successfully! Your PNR is: {booking.pnr_code}",
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
        booking = get_object_or_404(
            Booking, pk=kwargs["pk"], customer=self.request.user
        )
        context["booking"] = booking
        return context

    def post(self, request, *args, **kwargs):
        booking = get_object_or_404(Booking, pk=kwargs["pk"], customer=request.user)
        payment_method = request.POST.get("payment_method")
        if payment_method:
            booking.payment_method = payment_method
            booking.status = "confirmed"
            booking.save()
            messages.success(request, "Payment successful! Your booking is confirmed.")
            return redirect("bookings:payment_success", pk=booking.pk)
        messages.error(request, "Please select a payment method.")
        return redirect("bookings:payment", pk=booking.pk)


class PaymentSuccessView(LoginRequiredMixin, DetailView):
    model = Booking
    template_name = "bookings/payment_success.html"
    context_object_name = "booking"

    def get_queryset(self):
        return Booking.objects.filter(customer=self.request.user)
