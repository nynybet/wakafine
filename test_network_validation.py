#!/usr/bin/env python
"""
Test script for new mobile money network validation
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine_bus.settings")
django.setup()

from bookings.views import PaymentView


def test_phone_normalization():
    """Test phone number normalization"""
    payment_view = PaymentView()

    test_cases = [
        # +232 format (should have 11 digits after +)
        ("+232076123456", "+232076123456"),  # Correct format
        ("+23276123456", "+232076123456"),  # Missing 0, should add it
        # 232 format
        ("232076123456", "+232076123456"),  # Add + prefix
        # Local format with 0
        ("076123456", "+232076123456"),  # 9 digits starting with 0
        # 8-digit format
        ("76123456", "+232076123456"),  # Add 0 and country code
        # Invalid formats
        ("123456", None),  # Too short
        ("0123456", None),  # Wrong network code
    ]

    print("=== Phone Number Normalization Tests ===")
    for input_phone, expected in test_cases:
        result = payment_view.normalize_phone_number(input_phone)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        print(f"{status} {input_phone} -> {result} (expected: {expected})")


def test_network_validation():
    """Test network compatibility validation"""
    payment_view = PaymentView()

    test_cases = [
        # Orange Money tests
        ("orange_money", "+232076123456", None),  # Valid Orange
        ("orange_money", "+232075123456", None),  # Valid Orange
        ("orange_money", "+232078123456", None),  # Valid Orange
        ("orange_money", "+232079123456", None),  # Valid Orange
        (
            "orange_money",
            "+232077123456",
            "Orange Money only works",
        ),  # Invalid - Africell number
        # Afrimoney tests
        ("afrimoney", "+232077123456", None),  # Valid Africell
        ("afrimoney", "+232080123456", None),  # Valid Africell
        ("afrimoney", "+232088123456", None),  # Valid Africell
        ("afrimoney", "+232030123456", None),  # Valid Africell
        ("afrimoney", "+232033123456", None),  # Valid Africell
        ("afrimoney", "+232099123456", None),  # Valid Africell
        (
            "afrimoney",
            "+232076123456",
            "Afrimoney only works",
        ),  # Invalid - Orange number
        # Qmoney tests
        ("qmoney", "+232031123456", None),  # Valid Qcell
        ("qmoney", "+232032123456", None),  # Valid Qcell
        ("qmoney", "+232034123456", None),  # Valid Qcell
        ("qmoney", "+232076123456", "Qmoney only works"),  # Invalid - Orange number
    ]

    print("\n=== Network Compatibility Tests ===")
    for payment_method, phone, expected_error in test_cases:
        result = payment_view.validate_network_compatibility(payment_method, phone)

        if expected_error is None:
            # Should be valid (no error)
            status = "✅ PASS" if result is None else "❌ FAIL"
            print(f"{status} {payment_method} + {phone} -> Valid (expected: Valid)")
        else:
            # Should have error
            status = "✅ PASS" if result and expected_error in result else "❌ FAIL"
            print(
                f"{status} {payment_method} + {phone} -> Error detected (expected: Error)"
            )
            if result:
                print(f"      Error: {result}")


if __name__ == "__main__":
    test_phone_normalization()
    test_network_validation()
    print("\n=== Test Complete ===")
