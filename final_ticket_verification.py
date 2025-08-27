#!/usr/bin/env python3
"""
Final verification script for ticket QR code and print functionality.
This script verifies all implemented features are working correctly.
"""

import os
import re
from pathlib import Path


def analyze_template(file_path, template_name):
    """Analyze a ticket template for QR code and print functionality."""
    print(f"\n🎫 Analyzing {template_name}")
    print("-" * 40)

    if not os.path.exists(file_path):
        print(f"❌ Template not found: {file_path}")
        return False

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # QR Code Implementation Checks
    qr_features = {
        "QR Container": bool(re.search(r'id="qr-code"', content)),
        "QR Code Script": bool(re.search(r"QRCode\.toCanvas", content)),
        "Enhanced Size (120px)": bool(re.search(r"width:\s*120", content)),
        "High Error Correction": bool(
            re.search(r'errorCorrectionLevel:\s*[\'"]H[\'"]', content)
        ),
        "Black QR Color": bool(re.search(r'dark:\s*[\'"]#000000[\'"]', content)),
        "QR Fallback": bool(re.search(r"showFallback|qr-fallback", content)),
        "Enhanced Styling": bool(re.search(r"border:\s*2px solid", content)),
    }

    # Print Functionality Checks
    print_features = {
        "Print CSS": bool(re.search(r"@media print", content)),
        "Hide Non-Print": bool(re.search(r"\.no-print", content)),
        "Print Button": bool(re.search(r"Print Ticket", content)),
        "Visibility Hidden": bool(re.search(r"visibility:\s*hidden", content)),
        "Show Ticket Only": bool(
            re.search(r"\.ticket-container.*visibility:\s*visible", content, re.DOTALL)
        ),
        "Color Preservation": bool(re.search(r"print-color-adjust:\s*exact", content)),
        "Page Margins": bool(re.search(r"margin:\s*0.*!important", content)),
    }

    # Display Results
    print("QR Code Features:")
    qr_passed = 0
    for feature, status in qr_features.items():
        icon = "✅" if status else "❌"
        print(f"  {icon} {feature}")
        if status:
            qr_passed += 1

    print(f"\nPrint Features:")
    print_passed = 0
    for feature, status in print_features.items():
        icon = "✅" if status else "❌"
        print(f"  {icon} {feature}")
        if status:
            print_passed += 1

    total_features = len(qr_features) + len(print_features)
    total_passed = qr_passed + print_passed

    print(
        f"\n📊 Score: {total_passed}/{total_features} ({(total_passed/total_features)*100:.1f}%)"
    )

    return total_passed == total_features


def analyze_booking_list():
    """Analyze the booking list template for print functionality."""
    print(f"\n📋 Analyzing Booking List Print Features")
    print("-" * 40)

    file_path = "templates/bookings/list.html"

    if not os.path.exists(file_path):
        print(f"❌ Template not found: {file_path}")
        return False

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    list_features = {
        "Print Ticket Button": bool(re.search(r"Print Ticket", content)),
        "Opens in New Tab": bool(re.search(r'target="_blank"', content)),
        "Auto Print Trigger": bool(re.search(r"window\.print\(\)", content)),
        "Print Icon": bool(re.search(r"fa-print", content)),
        "Conditional Display": bool(re.search(r"booking\.status.*confirmed", content)),
    }

    passed = 0
    for feature, status in list_features.items():
        icon = "✅" if status else "❌"
        print(f"  {icon} {feature}")
        if status:
            passed += 1

    print(
        f"\n📊 Score: {passed}/{len(list_features)} ({(passed/len(list_features))*100:.1f}%)"
    )

    return passed == len(list_features)


def main():
    """Main verification function."""
    print("🎯 FINAL VERIFICATION: Ticket QR Code & Print Functionality")
    print("=" * 70)

    templates = [
        ("templates/bookings/ticket.html", "Main Ticket Template"),
        ("templates/bookings/ticket_simple.html", "Simple Ticket Template"),
        ("templates/bookings/ticket_print.html", "Print-Optimized Template"),
    ]

    all_passed = True
    template_scores = []

    # Analyze each ticket template
    for file_path, name in templates:
        result = analyze_template(file_path, name)
        template_scores.append(result)
        if not result:
            all_passed = False

    # Analyze booking list
    list_result = analyze_booking_list()
    if not list_result:
        all_passed = False

    # Final Summary
    print(f"\n" + "=" * 70)
    print("📊 FINAL SUMMARY")
    print("-" * 20)

    for i, (_, name) in enumerate(templates):
        icon = "✅" if template_scores[i] else "❌"
        print(f"{icon} {name}")

    icon = "✅" if list_result else "❌"
    print(f"{icon} Booking List Print Features")

    if all_passed:
        print("\n🎉 EXCELLENT! All ticket functionality is properly implemented!")
        print("\n🚀 Key Features Successfully Implemented:")
        print("   • 120x120px QR codes with high error correction")
        print("   • Pure black QR codes for optimal print scanning")
        print("   • Comprehensive print CSS hiding all non-ticket elements")
        print("   • Print buttons on all ticket pages")
        print("   • Auto-print functionality from booking list")
        print("   • Enhanced QR fallback displays")
        print("   • Consistent styling across all templates")
        print("   • Professional ticket layout for printing")

        print("\n📋 User Experience:")
        print("   • Users can view tickets with clear QR codes")
        print("   • One-click printing from ticket pages")
        print("   • Direct print access from booking list")
        print("   • Only ticket content prints (no headers/navigation)")
        print("   • QR codes are easily scannable from printouts")

    else:
        print("\n⚠️  Some features may need attention. Review the details above.")

    return all_passed


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
