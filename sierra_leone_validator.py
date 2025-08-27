#!/usr/bin/env python
"""
Sierra Leone Mobile Money Validation System
Uses specific regex patterns for each provider
"""

import re
from typing import Optional, Tuple


class SierraLeoneMobileValidator:
    """
    Comprehensive validator for Sierra Leone mobile money numbers
    Uses specific regex patterns for each provider
    """

    # Regex patterns for each mobile money provider
    PROVIDER_PATTERNS = {
        "orange": r"^\+232(76|75|78|79)\d{6}$|^0(76|75|78|79)\d{6}$",
        "afrimoney": r"^\+232(30|33|99|77|80|88)\d{6}$|^0(30|33|99|77|80|88)\d{6}$",
        "qmoney": r"^\+232(31|32|34)\d{6}$|^0(31|32|34)\d{6}$",
    }

    # Network code mappings for reference
    NETWORK_CODES = {
        "orange": {
            "international": ["76", "75", "78", "79"],
            "local": ["076", "075", "078", "079"],
        },
        "afrimoney": {
            "international": ["30", "33", "99", "77", "80", "88"],
            "local": ["030", "033", "099", "077", "080", "088"],
        },
        "qmoney": {"international": ["31", "32", "34"], "local": ["031", "032", "034"]},
    }

    @classmethod
    def validate_number(
        cls, phone_number: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validate a phone number and determine its provider using regex patterns

        Returns:
            (is_valid, provider, normalized_number)
        """
        if not phone_number:
            return False, None, None

        # Clean the phone number (remove spaces, dashes, etc.)
        clean_number = re.sub(r"[^0-9+]", "", phone_number)

        # Test against each provider's regex pattern
        for provider, pattern in cls.PROVIDER_PATTERNS.items():
            if re.match(pattern, clean_number):
                # Normalize to +232 format
                normalized = cls._normalize_to_international(clean_number)
                return True, provider, normalized

        return False, None, None

    @classmethod
    def _normalize_to_international(cls, number: str) -> str:
        """
        Normalize phone number to +232 format
        """
        if number.startswith("+232"):
            return number
        elif number.startswith("0"):
            # Convert local format to international: 076123456 -> +23276123456
            return f"+232{number[1:]}"
        else:
            return number

    @classmethod
    def validate_for_provider(cls, phone_number: str, provider: str) -> bool:
        """
        Validate if a phone number matches a specific provider's pattern

        Args:
            phone_number: The phone number to validate
            provider: The provider to check against ('orange', 'afrimoney', 'qmoney')

        Returns:
            True if the number matches the provider's pattern, False otherwise
        """
        if not phone_number or provider not in cls.PROVIDER_PATTERNS:
            return False

        # Clean the phone number
        clean_number = re.sub(r"[^0-9+]", "", phone_number)

        # Test against the specific provider's pattern
        pattern = cls.PROVIDER_PATTERNS[provider]
        return bool(re.match(pattern, clean_number))

    @classmethod
    def get_provider_for_payment_method(cls, payment_method: str) -> Optional[str]:
        """Map payment method to provider name"""
        mapping = {
            "orange_money": "orange",
            "afrimoney": "afrimoney",
            "qmoney": "qmoney",
        }
        return mapping.get(payment_method)

    @classmethod
    def validate_payment_compatibility(
        cls, payment_method: str, phone_number: str
    ) -> Optional[str]:
        """
        Check if phone number is compatible with payment method
        Returns error message if incompatible, None if compatible
        """
        is_valid, detected_provider, normalized = cls.validate_number(phone_number)

        if not is_valid:
            return "Invalid phone number format. Please enter a valid Sierra Leone mobile number."

        expected_provider = cls.get_provider_for_payment_method(payment_method)
        if not expected_provider:
            return f"Unknown payment method: {payment_method}"

        if detected_provider != expected_provider:
            provider_name = payment_method.replace("_", " ").title()

            if expected_provider == "orange":
                valid_codes = (
                    "76, 75, 78, 79 (+232 format) or 076, 075, 078, 079 (local format)"
                )
            elif expected_provider == "afrimoney":
                valid_codes = "30, 33, 99, 77, 80, 88 (+232 format) or 030, 033, 099, 077, 080, 088 (local format)"
            else:  # qmoney
                valid_codes = "31, 32, 34 (+232 format) or 031, 032, 034 (local format)"

            return (
                f"{provider_name} only works with numbers starting with {valid_codes}."
            )

        return None

    @classmethod
    def normalize_number(cls, phone_number: str) -> Optional[str]:
        """
        Normalize phone number to +232 format
        Returns None if invalid
        """
        is_valid, provider, normalized = cls.validate_number(phone_number)
        return normalized if is_valid else None


def test_validator():
    """Test the validator with various inputs"""

    test_cases = [
        # Valid international format
        ("+23276123456", True, "orange"),  # Orange
        ("+23275123456", True, "orange"),  # Orange
        ("+23278123456", True, "orange"),  # Orange
        ("+23279123456", True, "orange"),  # Orange
        ("+23230123456", True, "afrimoney"),  # Afrimoney
        ("+23233123456", True, "afrimoney"),  # Afrimoney
        ("+23299123456", True, "afrimoney"),  # Afrimoney
        ("+23277123456", True, "afrimoney"),  # Afrimoney
        ("+23280123456", True, "afrimoney"),  # Afrimoney
        ("+23288123456", True, "afrimoney"),  # Afrimoney
        ("+23231123456", True, "qmoney"),  # Qmoney
        ("+23232123456", True, "qmoney"),  # Qmoney
        ("+23234123456", True, "qmoney"),  # Qmoney
        # Valid local format (9 digits: 3-digit code + 6 digits)
        ("076123456", True, "orange"),  # Orange
        ("075123456", True, "orange"),  # Orange
        ("078123456", True, "orange"),  # Orange
        ("079123456", True, "orange"),  # Orange
        ("030123456", True, "afrimoney"),  # Afrimoney
        ("033123456", True, "afrimoney"),  # Afrimoney
        ("099123456", True, "afrimoney"),  # Afrimoney
        ("077123456", True, "afrimoney"),  # Afrimoney
        ("080123456", True, "afrimoney"),  # Afrimoney
        ("088123456", True, "afrimoney"),  # Afrimoney
        ("031123456", True, "qmoney"),  # Qmoney
        ("032123456", True, "qmoney"),  # Qmoney
        ("034123456", True, "qmoney"),  # Qmoney
        # Invalid formats
        ("+232012345", False, None),  # Starts with 0 after +232
        ("+23276", False, None),  # Too short
        ("+232761234567", False, None),  # Too long
        ("+23281123456", False, None),  # Invalid network code 81
        ("076", False, None),  # Too short local
        ("0761234567", False, None),  # Too long local (should be 9 digits)
        ("176123456", False, None),  # Doesn't start with 0
        ("081123456", False, None),  # Invalid local network code
        ("", False, None),  # Empty
        ("abcd", False, None),  # Non-numeric
    ]

    print("=== Sierra Leone Mobile Money Validation Test ===\n")

    passed = 0
    total = len(test_cases)

    for number, expected_valid, expected_provider in test_cases:
        is_valid, provider, normalized = SierraLeoneMobileValidator.validate_number(
            number
        )

        test_passed = is_valid == expected_valid and provider == expected_provider
        status = "✅ PASS" if test_passed else "❌ FAIL"

        print(
            f"{status} {number:<15} -> Valid: {is_valid:<5} Provider: {str(provider):<10} Normalized: {normalized or 'None'}"
        )

        if test_passed:
            passed += 1
        else:
            print(
                f"     Expected: Valid: {expected_valid}, Provider: {expected_provider}"
            )

    print(f"\n=== Results: {passed}/{total} tests passed ===")

    # Test provider-specific validation
    print("\n=== Provider-Specific Validation Test ===")
    provider_tests = [
        ("076123456", "orange", True),  # Orange number with Orange provider
        ("076123456", "afrimoney", False),  # Orange number with Afrimoney provider
        ("030123456", "afrimoney", True),  # Afrimoney number with Afrimoney provider
        ("030123456", "qmoney", False),  # Afrimoney number with Qmoney provider
        ("031123456", "qmoney", True),  # Qmoney number with Qmoney provider
        ("031123456", "orange", False),  # Qmoney number with Orange provider
        ("+23276123456", "orange", True),  # International Orange number
        ("+23230123456", "afrimoney", True),  # International Afrimoney number
        ("+23231123456", "qmoney", True),  # International Qmoney number
    ]

    for number, provider, expected in provider_tests:
        result = SierraLeoneMobileValidator.validate_for_provider(number, provider)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        print(
            f"{status} {number:<15} for {provider:<10} -> {result} (expected {expected})"
        )

    # Test payment compatibility
    print("\n=== Payment Compatibility Test ===")
    compatibility_tests = [
        ("orange_money", "076123456", None),  # Compatible
        (
            "orange_money",
            "030123456",
            "Orange Money only works with numbers starting with 76, 75, 78, 79 (+232 format) or 076, 075, 078, 079 (local format).",
        ),  # Incompatible
        ("afrimoney", "030123456", None),  # Compatible
        (
            "afrimoney",
            "076123456",
            "Afrimoney only works with numbers starting with 30, 33, 99, 77, 80, 88 (+232 format) or 030, 033, 099, 077, 080, 088 (local format).",
        ),  # Incompatible
        ("qmoney", "031123456", None),  # Compatible
        (
            "qmoney",
            "076123456",
            "Qmoney only works with numbers starting with 31, 32, 34 (+232 format) or 031, 032, 034 (local format).",
        ),  # Incompatible
    ]

    for payment_method, number, expected_error in compatibility_tests:
        error = SierraLeoneMobileValidator.validate_payment_compatibility(
            payment_method, number
        )
        status = "✅ PASS" if error == expected_error else "❌ FAIL"
        print(
            f"{status} {payment_method:<15} + {number:<12} -> {error or 'Compatible'}"
        )


if __name__ == "__main__":
    test_validator()
