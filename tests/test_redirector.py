import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock

from service.redirector import RedirectorService, NotFoundError, GoneError
from model.url_mapping import URLMapping

@pytest.fixture
def redirector():
    # Create a RedirectorService with a mocked repository
    service = RedirectorService()
    service.repo = MagicMock()
    return service

class TestRedirectorService:

    def test_redirect_success(self, redirector):
        # Setup mock mapping
        mock_mapping = MagicMock()
        mock_mapping.long_url = "https://example.com"
        mock_mapping.expires_at = None

        # Configure the mock repo to return our mock mapping
        redirector.repo.get_mapping_by_key.return_value = mock_mapping

        # Test the redirect method
        result = redirector.redirect("abc123")

        # Verify the result
        assert result == "https://example.com"
        redirector.repo.get_mapping_by_key.assert_called_once_with(short_key="abc123")

    def test_redirect_not_found(self, redirector):
        # Configure the mock repo to return None (mapping not found)
        redirector.repo.get_mapping_by_key.return_value = None

        # Test that NotFoundError is raised
        with pytest.raises(NotFoundError) as excinfo:
            redirector.redirect("nonexistent")

        # Verify the error message
        assert "No mapping for key 'nonexistent'" in str(excinfo.value)
        redirector.repo.get_mapping_by_key.assert_called_once_with(short_key="nonexistent")

    def test_redirect_expired(self, redirector):
        # Setup mock mapping with expired timestamp
        mock_mapping = MagicMock()
        mock_mapping.long_url = "https://example.com"
        mock_mapping.expires_at = datetime.now(timezone.utc) - timedelta(days=1)  # Expired yesterday

        # Configure the mock repo to return our expired mock mapping
        redirector.repo.get_mapping_by_key.return_value = mock_mapping

        # Test that GoneError is raised
        with pytest.raises(GoneError) as excinfo:
            redirector.redirect("expired")

        # Verify the error message contains "expired"
        assert "expired" in str(excinfo.value)
        redirector.repo.get_mapping_by_key.assert_called_once_with(short_key="expired")

    def test_redirect_future_expiry(self, redirector):
        # Setup mock mapping with future expiry
        mock_mapping = MagicMock()
        mock_mapping.long_url = "https://example.com"
        mock_mapping.expires_at = datetime.now(timezone.utc) + timedelta(days=1)  # Expires tomorrow

        # Configure the mock repo to return our mock mapping
        redirector.repo.get_mapping_by_key.return_value = mock_mapping

        # Test the redirect method
        result = redirector.redirect("future")

        # Verify the result
        assert result == "https://example.com"
        redirector.repo.get_mapping_by_key.assert_called_once_with(short_key="future")
