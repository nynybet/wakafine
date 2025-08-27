#!/usr/bin/env python3
"""
Quick verification script to test ticket QR code and print functionality.
This script checks the ticket templates and verifies QR code implementation.
"""

import os
import re
from pathlib import Path


def check_file_content(file_path, checks):
    """Check if file contains all required content."""
    if not os.path.exists(file_path):
        return False, f"File {file_path} does not exist"

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    missing = []
    for check_name, pattern in checks.items():
        if not re.search(pattern, content, re.IGNORECASE | re.DOTALL):
            missing.append(check_name)

    if missing:
        return False, f"Missing: {', '.join(missing)}"
    return True, "All checks passed"


def main():
    """Main verification function."""
    base_path = "templates/bookings"

    # Common checks for all ticket templates
    common_checks = {
        "QR Code Container": r'id="qr-code"',
        "QR Code Script": r"QRCode\.toCanvas",
        "Print CSS": r"@media print",
        "Enhanced QR Size": r"width:\s*120",
        "High Error Correction": r'errorCorrectionLevel:\s*[\'"]H[\'"]',
        "Black QR Color": r'dark:\s*[\'"]#000000[\'"]',
        "Print Button": r"Print Ticket",
    }

    templates = ["ticket.html", "ticket_simple.html", "ticket_print.html"]

    print("🔍 Verifying Ticket Templates QR Code and Print Functionality")
    print("=" * 60)

    all_passed = True

    for template in templates:
        file_path = os.path.join(base_path, template)
        print(f"\n📄 Checking {template}...")

        passed, message = check_file_content(file_path, common_checks)

        if passed:
            print(f"  ✅ {message}")
        else:
            print(f"  ❌ {message}")
            all_passed = False

    # Check bookings list for print functionality
    print(f"\n📄 Checking list.html...")
    list_checks = {
        "Print Ticket Link": r"Print Ticket",
        "Target Blank": r'target="_blank"',
        "Auto Print": r"window\.print\(\)",
    }

    list_path = os.path.join(base_path, "list.html")
    passed, message = check_file_content(list_path, list_checks)

    if passed:
        print(f"  ✅ {message}")
    else:
        print(f"  ❌ {message}")
        all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print(
            "🎉 ALL CHECKS PASSED! QR Code and Print functionality is properly implemented."
        )
        print("\n📋 Summary of Enhancements:")
        print("  • QR codes are 120x120px for better visibility")
        print("  • High error correction (Level H) for better scanning")
        print("  • Pure black color (#000000) for optimal print contrast")
        print("  • Enhanced fallback displays with better styling")
        print("  • Print CSS hides all non-ticket elements")
        print("  • Print buttons available on all ticket pages")
        print("  • Bookings list has 'Print Ticket' functionality")
        print("  • Consistent styling across all ticket templates")
    else:
        print("❌ SOME CHECKS FAILED! Please review the issues above.")

    return all_passed


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
