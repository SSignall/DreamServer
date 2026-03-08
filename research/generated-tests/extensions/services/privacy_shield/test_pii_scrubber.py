"""
=== GENERATED TEST FILE — NEEDS REVIEW ===
Generated: 2026-03-08T02:32:00.389460+00:00
Source: extensions/services/privacy_shield/pii_scrubber.py
Generator: Qwen3-Coder (local GPU)

This file was auto-generated and has NOT been reviewed or run.
Review before using. May need fixture adjustments or mock updates.
================================================================
"""

import pytest
import re
from unittest.mock import Mock, patch
from extensions.services.privacy_shield.pii_scrubber import PIIDetector, PrivacyShield


class TestPIIDetector:
    @pytest.fixture
    def detector(self):
        # Use a fixed session token for deterministic tests
        with patch.object(PIIDetector, '__init__', lambda self: None):
            d = PIIDetector()
            d.token_prefix = "<PII_"
            d.token_suffix = ">"
            d.pii_map = {}
            d.counter = 0
            d.session_token = "test_session_token_12345"
            d.PATTERNS = PIIDetector.PATTERNS.copy()
            return d

    def test_init_default_values(self):
        detector = PIIDetector()
        assert detector.token_prefix == "<PII_"
        assert detector.token_suffix == ">"
        assert isinstance(detector.pii_map, dict)
        assert detector.counter == 0
        assert len(detector.session_token) == 32  # hex(16) = 32 chars

    def test_generate_token_deterministic(self, detector):
        pii_type = "email"
        original = "test@example.com"
        
        token1 = detector._generate_token(pii_type, original)
        token2 = detector._generate_token(pii_type, original)
        
        assert token1 == token2
        assert token1.startswith(detector.token_prefix)
        assert token1.endswith(detector.token_suffix)
        assert pii_type in token1

    def test_generate_token_different_inputs(self, detector):
        token1 = detector._generate_token("email", "user1@example.com")
        token2 = detector._generate_token("email", "user2@example.com")
        token3 = detector._generate_token("phone", "123-456-7890")
        
        assert token1 != token2 != token3

    def test_scrub_email(self, detector):
        text = "Contact me at john.doe@example.com"
        result = detector.scrub(text)
        
        assert "john.doe@example.com" not in result
        assert "<PII_email_" in result
        assert result.count("<PII_email_") == 1

    def test_scrub_phone(self, detector):
        text = "Call me at 555-123-4567 or 1-800-555-1234"
        result = detector.scrub(text)
        
        assert "555-123-4567" not in result
        assert "1-800-555-1234" not in result
        assert result.count("<PII_phone_") == 2

    def test_scrub_ssn(self, detector):
        text = "My SSN is 123-45-6789 and yours is 987.65.4321"
        result = detector.scrub(text)
        
        assert "123-45-6789" not in result
        assert "987.65.4321" not in result
        assert result.count("<PII_ssn_") == 2

    def test_scrub_ip_address(self, detector):
        text = "Server IP: 192.168.1.100 and 10.0.0.1"
        result = detector.scrub(text)
        
        assert "192.168.1.100" not in result
        assert "10.0.0.1" not in result
        assert result.count("<PII_ip_address_") == 2

    def test_scrub_ipv6_address(self, detector):
        text = "IPv6: 2001:0db8:85a3:0000:0000:8a2e:0370:7334"
        result = detector.scrub(text)
        
        assert "2001:0db8:85a3:0000:0000:8a2e:0370:7334" not in result
        assert result.count("<PII_ip_address_") == 1

    def test_scrub_api_key(self, detector):
        text = "API Key: sk-abc123xyz789abcdef and apikey=secret1234567890"
        result = detector.scrub(text)
        
        assert "sk-abc123xyz789abcdef" not in result
        assert "secret1234567890" not in result
        assert result.count("<PII_api_key_") == 2

    def test_scrub_credit_card(self, detector):
        text = "Card: 1234-5678-9012-3456 and 1234 5678 9012 3456"
        result = detector.scrub(text)
        
        assert "1234-5678-9012-3456" not in result
        assert "1234 5678 9012 3456" not in result
        assert result.count("<PII_credit_card_") == 2

    def test_scrub_multiple_pii_types(self, detector):
        text = """
        Contact: john.doe@example.com
        Phone: 555-123-4567
        SSN: 123-45-6789
        IP: 192.168.1.100
        """
        result = detector.scrub(text)
        
        assert "john.doe@example.com" not in result
        assert "555-123-4567" not in result
        assert "123-45-6789" not in result
        assert "192.168.1.100" not in result
        assert result.count("<PII_") == 4

    def test_scrub_duplicate_pii_same_token(self, detector):
        text1 = "Email: user@example.com"
        text2 = "Also: user@example.com"
        
        result1 = detector.scrub(text1)
        result2 = detector.scrub(text2)
        
        # Extract the token from first result
        token = re.search(r'<PII_email_[^>]+>', result1).group(0)
        
        assert token in result2
        assert result2.count(token) == 1

    def test_restore(self, detector):
        original_text = "Contact: john.doe@example.com"
        scrubbed = detector.scrub(original_text)
        restored = detector.restore(scrubbed)
        
        assert restored == original_text

    def test_restore_multiple_pii(self, detector):
        text = "Email: john@example.com, Phone: 555-123-4567"
        scrubbed = detector.scrub(text)
        restored = detector.restore(scrubbed)
        
        assert restored == text

    def test_restore_with_unknown_token(self, detector):
        text = "Contact: <PII_email_unknown12345678>"
        restored = detector.restore(text)
        
        # Unknown tokens should remain unchanged
        assert restored == text

    def test_get_stats(self, detector):
        text = "Email: john@example.com, Phone: 555-123-4567"
        detector.scrub(text)
        stats = detector.get_stats()
        
        assert stats['unique_pii_count'] == 2
        assert 'email' in stats['pii_types']
        assert 'phone' in stats['pii_types']

    def test_get_stats_empty(self, detector):
        stats = detector.get_stats()
        
        assert stats['unique_pii_count'] == 0
        assert stats['pii_types'] == []

    def test_scrub_preserves_non_pii_text(self, detector):
        text = "Hello world! This is a test without any PII."
        result = detector.scrub(text)
        
        assert result == text

    def test_scrub_case_insensitive_api_key(self, detector):
        text = "APIKEY: secret1234567890 and Api-Key: anothersecret1234567890"
        result = detector.scrub(text)
        
        assert "secret1234567890" not in result
        assert "anothersecret1234567890" not in result
        assert result.count("<PII_api_key_") == 2


class TestPrivacyShield:
    @pytest.fixture
    def shield(self):
        return PrivacyShield()

    def test_process_request_scrubs_pii(self, shield):
        prompt = "Contact: john@example.com"
        scrubbed, metadata = shield.process_request(prompt)
        
        assert "john@example.com" not in scrubbed
        assert metadata['scrubbed'] is True
        assert metadata['pii_count'] == 1

    def test_process_request_no_pii(self, shield):
        prompt = "Hello world! No PII here."
        scrubbed, metadata = shield.process_request(prompt)
