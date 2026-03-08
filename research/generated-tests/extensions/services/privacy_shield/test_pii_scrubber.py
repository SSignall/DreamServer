"""
=== GENERATED TEST FILE — NEEDS REVIEW ===
Generated: 2026-03-08T02:00:21.090508+00:00
Source: extensions/services/privacy-shield/pii_scrubber.py
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
            d.session_token = "fixed_session_token_12345"
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
        assert token1.startswith("<PII_email_")
        assert token1.endswith(">")
        # Token format: <PII_<type>_<hash>_<session_token>_<counter>>
        # Hash length should be at least 8 characters for reasonable uniqueness
        hash_start = len("<PII_email_")
        hash_end = token1.find("_", hash_start)
        hash_length = hash_end - hash_start if hash_end > hash_start else 0
        assert hash_length >= 8, f"Hash length {hash_length} is too short for uniqueness"

    def test_generate_token_different_inputs(self, detector):
        token1 = detector._generate_token("email", "a@b.com")
        token2 = detector._generate_token("email", "c@d.com")
        token3 = detector._generate_token("phone", "a@b.com")
        
        assert token1 != token2
        assert token1 != token3
        assert token2 != token3

    def test_scrub_email(self, detector):
        text = "Contact me at john.doe@example.com"
        scrubbed = detector.scrub(text)
        
        assert "john.doe@example.com" not in scrubbed
        assert "<PII_email_" in scrubbed
        assert len(detector.pii_map) == 1

    def test_scrub_phone(self, detector):
        text = "Call me at 555-123-4567 or (555) 123-4567"
        scrubbed = detector.scrub(text)
        
        assert "555-123-4567" not in scrubbed
        assert "(555) 123-4567" not in scrubbed
        assert "<PII_phone_" in scrubbed
        assert len(detector.pii_map) == 2

    def test_scrub_ssn(self, detector):
        text = "My SSN is 123-45-6789"
        scrubbed = detector.scrub(text)
        
        assert "123-45-6789" not in scrubbed
        assert "<PII_ssn_" in scrubbed
        assert len(detector.pii_map) == 1

    def test_scrub_ip_address(self, detector):
        text = "Server IP: 192.168.1.100 and 10.0.0.1"
        scrubbed = detector.scrub(text)
        
        assert "192.168.1.100" not in scrubbed
        assert "10.0.0.1" not in scrubbed
        assert "<PII_ip_address_" in scrubbed
        assert len(detector.pii_map) == 2

    def test_scrub_ipv6(self, detector):
        text = "IPv6: 2001:0db8:85a3:0000:0000:8a2e:0370:7334"
        scrubbed = detector.scrub(text)
        
        assert "2001:0db8:85a3:0000:0000:8a2e:0370:7334" not in scrubbed
        assert "<PII_ip_address_" in scrubbed
        assert len(detector.pii_map) == 1

    def test_scrub_api_key(self, detector):
        text = "API Key: sk-abc123xyz789abcdef"
        scrubbed = detector.scrub(text)
        
        assert "sk-abc123xyz789abcdef" not in scrubbed
        assert "<PII_api_key_" in scrubbed
        assert len(detector.pii_map) == 1

    def test_scrub_credit_card(self, detector):
        text = "Card: 4111-1111-1111-1111 or 4111 1111 1111 1111"
        scrubbed = detector.scrub(text)
        
        assert "4111-1111-1111-1111" not in scrubbed
        assert "4111 1111 1111 1111" not in scrubbed
        assert "<PII_credit_card_" in scrubbed
        assert len(detector.pii_map) == 2

    def test_scrub_multiple_pii_types(self, detector):
        text = """
        Email: john@example.com
        Phone: 555-123-4567
        SSN: 123-45-6789
        """
        scrubbed = detector.scrub(text)
        
        assert "john@example.com" not in scrubbed
        assert "555-123-4567" not in scrubbed
        assert "123-45-6789" not in scrubbed
        assert scrubbed.count("<PII_") == 3
        assert len(detector.pii_map) == 3

    def test_scrub_deterministic_same_pii(self, detector):
        text1 = "Email: john@example.com"
        text2 = "Contact john@example.com"
        
        scrubbed1 = detector.scrub(text1)
        scrubbed2 = detector.scrub(text2)
        
        # Extract the token from both scrubbed texts
        token1 = re.search(r'<PII_email_[^>]+>', scrubbed1).group(0)
        token2 = re.search(r'<PII_email_[^>]+>', scrubbed2).group(0)
        
        assert token1 == token2
        assert len(detector.pii_map) == 1

    def test_restore(self, detector):
        text = "Email: john@example.com"
        scrubbed = detector.scrub(text)
        restored = detector.restore(scrubbed)
        
        assert restored == text

    def test_restore_multiple_pii(self, detector):
        text = """
        Email: john@example.com
        Phone: 555-123-4567
        SSN: 123-45-6789
        """
        scrubbed = detector.scrub(text)
        restored = detector.restore(scrubbed)
        
        assert restored.strip() == text.strip()

    def test_restore_unknown_token(self, detector):
        text = "Hello <PII_email_unknown123>"
        restored = detector.restore(text)
        
        # Unknown tokens should remain unchanged
        assert restored == text

    def test_get_stats(self, detector):
        detector.pii_map = {
            "<PII_email_abc123def456>": "john@example.com",
            "<PII_phone_789xyz012abc>": "555-123-4567",
            "<PII_ssn_def456ghi789>": "123-45-6789"
        }
        
        stats = detector.get_stats()
        
        assert stats['unique_pii_count'] == 3
        assert set(stats['pii_types']) == {'email', 'phone', 'ssn'}

    def test_get_stats_empty(self, detector):
        stats = detector.get_stats()
        assert stats['unique_pii_count'] == 0
        assert stats['pii_types'] == []

    def test_scrub_with_existing_tokens(self, detector):
        # First scrub
        text1 = "Email: john@example.com"
        scrubbed1 = detector.scrub(text1)
        
        # Second scrub with same PII
        text2 = "Also: john@example.com"
        scrubbed2 = detector.scrub(text2)
        
        # Extract token from first scrub
        token = re.search(r'<PII_email_[^>]+>', scrubbed1).group(0)
        
        # Verify same token used in second scrub
        assert token in scrubbed2
        assert len(detector.pii_map) == 1


class TestPrivacyShield:
    @pytest.fixture
    def shield(self):
        return PrivacyShield()

    def test_process_request_scrubs_pii(self, shield):
        prompt = "Email: john@example.com"
        scrubbed, metadata = shield.process_request(prompt
