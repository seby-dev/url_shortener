import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock

from service.url_generator import URLGeneratorService, InvalidURLError, AliasConflictError
from model.url_mapping import URLMapping
from repository.db_repo import DBRepository

@pytest.fixture
def url_generator():
    return URLGeneratorService()

class TestURLGeneratorService:
    
    def test_validate_url_valid(self, url_generator):
        # Should not raise an exception
        url_generator._validate_url("https://example.com")
        url_generator._validate_url("http://example.com/path?query=value")
        
    def test_validate_url_invalid(self, url_generator):
        with pytest.raises(InvalidURLError):
            url_generator._validate_url("not-a-url")
        
        with pytest.raises(InvalidURLError):
            url_generator._validate_url("ftp://example.com")
            
        with pytest.raises(InvalidURLError):
            url_generator._validate_url("https://")
    
    def test_make_random_key(self, url_generator):
        key = url_generator._make_random_key()
        assert len(key) == url_generator._key_length
        assert all(c in url_generator._alphabet for c in key)
        
        # Test uniqueness (probabilistic)
        keys = [url_generator._make_random_key() for _ in range(10)]
        assert len(set(keys)) == 10  # All keys should be unique
    
    def test_generate_with_custom_alias(self, url_generator):
        with patch.object(url_generator.repo, 'get_mapping_by_key', return_value=None), \
             patch.object(url_generator.repo, 'save_url_mapping'):
            
            short_key = url_generator.generate("https://example.com", custom_alias="test123")
            assert short_key == "test123"
    
    def test_generate_with_invalid_custom_alias(self, url_generator):
        with pytest.raises(InvalidURLError):
            url_generator.generate("https://example.com", custom_alias="t")  # Too short
            
        with pytest.raises(InvalidURLError):
            url_generator.generate("https://example.com", custom_alias="test12345")  # Too long
            
        with pytest.raises(InvalidURLError):
            url_generator.generate("https://example.com", custom_alias="test@123")  # Invalid character
    
    def test_generate_with_conflicting_alias(self, url_generator):
        with patch.object(url_generator.repo, 'get_mapping_by_key', return_value=URLMapping()):
            with pytest.raises(AliasConflictError):
                url_generator.generate("https://example.com", custom_alias="test123")
    
    def test_generate_with_random_key(self, url_generator):
        with patch.object(url_generator.repo, 'get_mapping_by_key', return_value=None), \
             patch.object(url_generator.repo, 'save_url_mapping'):
            
            short_key = url_generator.generate("https://example.com")
            assert len(short_key) == url_generator._key_length
    
    def test_generate_with_collision(self, url_generator):
        # Mock to simulate a collision on first attempt, then success
        def side_effect(key):
            if key == "collision":
                return URLMapping()
            return None
        
        with patch.object(url_generator, '_make_random_key', side_effect=["collision", "success"]), \
             patch.object(url_generator.repo, 'get_mapping_by_key', side_effect=side_effect), \
             patch.object(url_generator.repo, 'save_url_mapping'):
            
            short_key = url_generator.generate("https://example.com")
            assert short_key == "success"
    
    def test_generate_with_max_collisions(self, url_generator):
        # Mock to simulate reaching max collision retries
        with patch('service.url_generator.collision_retries', 3), \
             patch.object(url_generator, '_make_random_key', return_value="collision"), \
             patch.object(url_generator.repo, 'get_mapping_by_key', return_value=URLMapping()), \
             patch.object(url_generator.repo, 'save_url_mapping'):
            
            short_key = url_generator.generate("https://example.com")
            # Should create a longer key by concatenating two random keys
            assert len(short_key) > url_generator._key_length
    
    def test_generate_with_expiry(self, url_generator):
        future = datetime.now(timezone.utc) + timedelta(days=1)
        
        with patch.object(url_generator.repo, 'get_mapping_by_key', return_value=None), \
             patch.object(url_generator.repo, 'save_url_mapping') as mock_save:
            
            url_generator.generate("https://example.com", expires_at=future)
            # Verify the mapping was saved with the correct expiry
            args, _ = mock_save.call_args
            mapping = args[0]
            assert mapping.expires_at == future
    
    def test_generate_with_naive_datetime(self, url_generator):
        naive_datetime = datetime.now()  # No timezone
        
        with pytest.raises(ValueError):
            url_generator.generate("https://example.com", expires_at=naive_datetime)