import re
import secrets
import string
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.parse import urlparse

from model.url_mapping import URLMapping
from repository.db_repo import DBRepository
from util.config import collision_retries


#Custom exceptions
class AliasConflictError(Exception):
    pass

class InvalidURLError(Exception):
    pass

class URLGeneratorService:
    """
    Generates or validates a short key for a given long URL,
    persists the mapping and returns the full hosrt URL
    """

    _ALIAS_REGEX = re.compile(r'^[A-Za-z0-9]{4,8}$')

    def __init__(self):
        self.repo = DBRepository()
        self._alphabet = string.ascii_letters + string.digits
        self._key_length = 8

    def _validate_url(self, url: str):

        parts = urlparse(url)
        if parts.scheme not in ('http', 'https') or not parts.netloc:
            raise InvalidURLError(f"Invalid URL: {url}")


    def _make_random_key(self) -> str:
        return ''.join(secrets.choice(self._alphabet) for _ in range(self._key_length))

    def generate(self, long_url: str,
                 custom_alias: str = None,
                 expires_at: datetime = None) -> str:

        # Validate the URL
        self._validate_url(long_url)
        if expires_at:
            if expires_at.tzinfo is None:
                raise ValueError("expires_at must be timezone-aware")

        # Determine short_key
        if custom_alias:
            if not self._ALIAS_REGEX.fullmatch(custom_alias):
                raise InvalidURLError("Alias must be 4-8 alphanumeric characters")
            if self.repo.get_mapping_by_key(custom_alias):
                raise AliasConflictError(f"Alias {custom_alias} already in use")
            short_key = custom_alias
        else:
            for i in range(collision_retries):
                candidate = self._make_random_key()
                if not self.repo.get_mapping_by_key(candidate):
                    short_key = candidate
                    break
            else:
                # Fall back to longer key
                short_key = self._make_random_key() + self._make_random_key()


        # Build a domain object and save
        now = datetime.now(tz=ZoneInfo("UTC"))
        mapping = URLMapping(short_key=short_key, long_url=long_url, created_at=now, expires_at=expires_at)
        self.repo.save_url_mapping(mapping)

        return short_key


