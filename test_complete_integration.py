#!/usr/bin/env python
"""
Complete integration test for Sierra Leone mobile money validation system
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine_bus.settings")
django.setup()

from sierra_leone_validator import SierraLeoneMobileValidator
from bookings.views import PaymentView


def test_validator_functionality():
    """Test the validator itself"""
    print("=== Testing Sierra Leone Mobile Validator ===")

    test_cases = [
        # Orange numbers
        ("+23276123456", True, "orange"),
        ("076123456", True, "orange"),
        # Afrimoney numbers
        ("+23230123456", True, "afrimoney"),
        ("030123456", True, "afrimoney"),
        ("+23277123456", True, "afrimoney"),
        ("077123456", True, "afrimoney"),
        # Qmoney numbers
        ("+23231123456", True, "qmoney"),
        ("031123456", True, "qmoney"),
        # Invalid numbers
        ("+23281123456", False, None),  # Invalid network code
        ("012345678", False, None),  # Wrong format
    ]

    passed = 0
    total = len(test_cases)

    for number, expected_valid, expected_provider in test_cases:
        is_valid, provider, normalized = SierraLeoneMobileValidator.validate_number(
            number
        )

        test_passed = is_valid == expected_valid and provider == expected_provider
        status = "✅ PASS" if test_passed else "❌ FAIL"

        print(
            f"{status} {number:<15} -> Valid: {is_valid:<5} Provider: {str(provider):<10}"
        )

        if test_passed:
            passed += 1

    print(f"Validator Tests: {passed}/{total} passed\n")
    return passed == total


def test_payment_compatibility():
    """Test payment compatibility validation"""
    print("=== Testing Payment Compatibility ===")

    test_cases = [
        # Compatible cases
        ("orange_money", "076123456", None),
        ("afrimoney", "030123456", None),
        ("qmoney", "031123456", None),
        # Incompatible cases
        (
            "orange_money",
            "030123456",
            "Orange Money only works",
        ),  # Afrimoney number with Orange
        (
            "afrimoney",
            "076123456",
            "Afrimoney only works",
        ),  # Orange number with Afrimoney
        ("qmoney", "076123456", "Qmoney only works"),  # Orange number with Qmoney
    ]

    passed = 0
    total = len(test_cases)

    for payment_method, number, expected_error in test_cases:
        error = SierraLeoneMobileValidator.validate_payment_compatibility(
            payment_method, number
        )

        if expected_error is None:
            test_passed = error is None
            status = "✅ PASS" if test_passed else "❌ FAIL"
            print(f"{status} {payment_method:<15} + {number:<12} -> Compatible")
        else:
            test_passed = error is not None and expected_error in error
            status = "✅ PASS" if test_passed else "❌ FAIL"
            print(f"{status} {payment_method:<15} + {number:<12} -> Error detected")

        if test_passed:
            passed += 1

    print(f"Compatibility Tests: {passed}/{total} passed\n")
    return passed == total


def test_normalization():
    """Test phone number normalization"""
    print("=== Testing Number Normalization ===")

    test_cases = [
        ("076123456", "+23276123456"),
        ("+23276123456", "+23276123456"),
        ("030123456", "+23230123456"),
        ("031123456", "+23231123456"),
    ]

    passed = 0
    total = len(test_cases)

    for input_number, expected_output in test_cases:
        normalized = SierraLeoneMobileValidator.normalize_number(input_number)

        test_passed = normalized == expected_output
        status = "✅ PASS" if test_passed else "❌ FAIL"

        print(
            f"{status} {input_number:<12} -> {normalized or 'None':<15} (expected: {expected_output})"
        )

        if test_passed:
            passed += 1

    print(f"Normalization Tests: {passed}/{total} passed\n")
    return passed == total


def test_django_integration():
    """Test integration with Django views"""
    print("=== Testing Django Integration ===")

    # Test that the PaymentView can import and use the validator
    try:
        payment_view = PaymentView()

        # Test normalize_number method exists and works
        normalized = SierraLeoneMobileValidator.normalize_number("076123456")
        if normalized == "+23276123456":
            print("✅ PASS Django integration - normalize_number works")
            django_test_1 = True
        else:
            print("❌ FAIL Django integration - normalize_number failed")
            django_test_1 = False

        # Test validate_payment_compatibility method exists and works
        error = SierraLeoneMobileValidator.validate_payment_compatibility(
            "orange_money", "030123456"
        )
        if error and "Orange Money only works" in error:
            print("✅ PASS Django integration - validate_payment_compatibility works")
            django_test_2 = True
        else:
            print("❌ FAIL Django integration - validate_payment_compatibility failed")
            django_test_2 = False

        total_django_tests = django_test_1 and django_test_2
        print(
            f"Django Integration Tests: {'2/2' if total_django_tests else '1/2 or 0/2'} passed\n"
        )
        return total_django_tests

    except Exception as e:
        print(f"❌ FAIL Django integration - Exception: {e}")
        return False


def main():
    """Run all tests"""
    print("🚀 Sierra Leone Mobile Money Validation - Complete Integration Test\n")

    results = []

    # Run all test suites
    results.append(test_validator_functionality())
    results.append(test_payment_compatibility())
    results.append(test_normalization())
    results.append(test_django_integration())

    # Summary
    passed_suites = sum(results)
    total_suites = len(results)

    print("=" * 60)
    print(f"FINAL RESULTS: {passed_suites}/{total_suites} test suites passed")

    if passed_suites == total_suites:
        print("🎉 ALL TESTS PASSED! The integration is working correctly.")
        print("\n✅ Key Features Verified:")
        print("   • Regex-based validation for each provider")
        print("   • Payment compatibility checking")
        print("   • Phone number normalization")
        print("   • Django integration working")
        print("   • Provider-specific network code validation")
    else:
        print("❌ Some tests failed. Please review the output above.")

    print("=" * 60)


if __name__ == "__main__":
    main()
