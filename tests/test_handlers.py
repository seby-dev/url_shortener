import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock
from flask import json

from api.handlers import app, url_generator, redirector
from service.url_generator import InvalidURLError, AliasConflictError
from service.redirector import NotFoundError, GoneError

@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

class TestHandlers:
    
    def test_shorten_success(self, client):
        """Test successful URL shortening."""
        with patch.object(url_generator, 'generate', return_value='http://localhost:8000/abc123'):
            response = client.post('/shorten', 
                                  json={'long_url': 'https://example.com'})
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'short_url' in data
            assert data['short_url'] == 'http://localhost:8000/abc123'
    
    def test_shorten_with_alias(self, client):
        """Test URL shortening with a custom alias."""
        with patch.object(url_generator, 'generate', return_value='http://localhost:8000/custom'):
            response = client.post('/shorten', 
                                  json={'long_url': 'https://example.com', 'alias': 'custom'})
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['short_url'] == 'http://localhost:8000/custom'
            
    def test_shorten_with_expiry(self, client):
        """Test URL shortening with an expiration date."""
        expires_at = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        
        with patch.object(url_generator, 'generate', return_value='http://localhost:8000/abc123'):
            response = client.post('/shorten', 
                                  json={'long_url': 'https://example.com', 'expires_at': expires_at})
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['short_url'] == 'http://localhost:8000/abc123'
    
    def test_shorten_missing_long_url(self, client):
        """Test error handling when long_url is missing."""
        response = client.post('/shorten', json={})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Missing required field: long_url' in data['error']
    
    def test_shorten_invalid_url(self, client):
        """Test error handling for invalid URLs."""
        with patch.object(url_generator, 'generate', side_effect=InvalidURLError('Invalid URL')):
            response = client.post('/shorten', 
                                  json={'long_url': 'not-a-url'})
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'error' in data
            assert 'Invalid URL' in data['error']
    
    def test_shorten_alias_conflict(self, client):
        """Test error handling for alias conflicts."""
        with patch.object(url_generator, 'generate', 
                         side_effect=AliasConflictError("Alias 'custom' already in use")):
            response = client.post('/shorten', 
                                  json={'long_url': 'https://example.com', 'alias': 'custom'})
            
            assert response.status_code == 409
            data = json.loads(response.data)
            assert 'error' in data
            assert "Alias 'custom' already in use" in data['error']
    
    def test_shorten_invalid_expires_format(self, client):
        """Test error handling for invalid expires_at format."""
        response = client.post('/shorten', 
                              json={'long_url': 'https://example.com', 'expires_at': 'not-a-date'})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Invalid expires_at format' in data['error']
    
    def test_shorten_expires_without_timezone(self, client):
        """Test error handling for expires_at without timezone."""
        # Create a datetime without timezone
        naive_dt = datetime.now().isoformat()
        
        response = client.post('/shorten', 
                              json={'long_url': 'https://example.com', 'expires_at': naive_dt})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'expires_at must include a timezone offset' in data['error']
    
    def test_redirect_success(self, client):
        """Test successful redirection."""
        with patch.object(redirector, 'redirect', return_value='https://example.com'):
            response = client.get('/abc123')
            
            assert response.status_code == 302
            assert response.headers['Location'] == 'https://example.com'
    
    def test_redirect_not_found(self, client):
        """Test error handling for non-existent short keys."""
        with patch.object(redirector, 'redirect', side_effect=NotFoundError("No mapping for key 'nonexistent'")):
            response = client.get('/nonexistent')
            
            assert response.status_code == 404
            data = json.loads(response.data)
            assert 'error' in data
            assert 'Not Found' in data['error']
    
    def test_redirect_expired(self, client):
        """Test error handling for expired URLs."""
        with patch.object(redirector, 'redirect', side_effect=GoneError("URL for key 'expired' has expired")):
            response = client.get('/expired')
            
            assert response.status_code == 410
            data = json.loads(response.data)
            assert 'error' in data
            assert 'Gone' in data['error']
    
    def test_internal_server_error_shorten(self, client):
        """Test internal server error handling for shorten route."""
        with patch.object(url_generator, 'generate', side_effect=Exception('Unexpected error')):
            response = client.post('/shorten', 
                                  json={'long_url': 'https://example.com'})
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data
            assert 'Internal Server Error' in data['error']
    
    def test_internal_server_error_redirect(self, client):
        """Test internal server error handling for redirect route."""
        with patch.object(redirector, 'redirect', side_effect=Exception('Unexpected error')):
            response = client.get('/abc123')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data
            assert 'Internal Server Error' in data['error']