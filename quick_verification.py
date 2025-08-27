#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine_bus.settings")
django.setup()


def quick_verification():
    print("🔍 Quick verification of ticket system...")

    # 1. Check models
    from bookings.models import Booking

    try:
        booking = Booking.objects.get(id=21)
        print(f"✅ Booking exists: {booking.pnr_code}")
        print(f"   Customer: {booking.customer.username}")
        print(f"   Route: {booking.route}")
        print(f"   Travel Date: {booking.travel_date}")
    except Exception as e:
        print(f"❌ Booking error: {e}")
        return

    # 2. Check templates exist
    import os
    from django.conf import settings

    templates_dir = os.path.join(settings.BASE_DIR, "templates", "bookings")
    template_files = [
        "payment_success.html",
        "ticket.html",
        "ticket_print.html",
        "ticket_simple.html",
    ]

    print(f"\n📁 Template directory: {templates_dir}")
    for template in template_files:
        template_path = os.path.join(templates_dir, template)
        exists = os.path.exists(template_path)
        size = os.path.getsize(template_path) if exists else 0
        print(f"   {template}: {'✅' if exists else '❌'} ({size} bytes)")

    # 3. Check views can be imported
    try:
        from bookings.views import (
            PaymentSuccessView,
            TicketView,
            TicketPrintView,
            TicketPDFView,
        )

        print(f"\n✅ All views imported successfully")

        # Check view classes
        view_classes = [PaymentSuccessView, TicketView, TicketPrintView, TicketPDFView]
        for view_class in view_classes:
            print(f"   {view_class.__name__}: {view_class}")

    except Exception as e:
        print(f"❌ View import error: {e}")

    # 4. Check URLs
    try:
        from django.urls import reverse

        url_names = [
            ("bookings:payment_success", {"pk": booking.id}),
            ("bookings:ticket", {"pk": booking.id}),
            ("bookings:ticket_print", {"pk": booking.id}),
            ("bookings:ticket_pdf", {"pk": booking.id}),
        ]

        print(f"\n🔗 URL patterns:")
        for name, kwargs in url_names:
            try:
                url = reverse(name, kwargs=kwargs)
                print(f"   {name}: {url}")
            except Exception as e:
                print(f"   {name}: ❌ {e}")

    except Exception as e:
        print(f"❌ URL error: {e}")

    print(f"\n🎯 Verification complete!")
    print(f"💡 Manual testing:")
    print(f"   1. Visit http://127.0.0.1:8000/admin/ and login as admin")
    print(f"   2. Test URLs manually:")
    print(f"      - http://127.0.0.1:8000/bookings/payment/success/{booking.id}/")
    print(f"      - http://127.0.0.1:8000/bookings/{booking.id}/ticket/")
    print(f"      - http://127.0.0.1:8000/bookings/{booking.id}/ticket/print/")
    print(f"      - http://127.0.0.1:8000/bookings/{booking.id}/ticket/pdf/")


if __name__ == "__main__":
    quick_verification()
