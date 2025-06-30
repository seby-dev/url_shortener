from datetime import datetime, tzinfo
from zoneinfo import ZoneInfo

from repository.db_repo import DBRepository


# Custom exceptions
class NotFoundError(Exception):
    pass

class GoneError(Exception):
    pass

class RedirectorService:
    """
    Given a short key, looks up the mapping, enforces expiry, and returns the target long URL
    """
    def __init__(self):
        self.repo = DBRepository()

    def redirect(self, short_key: str) -> str:
        # Fetch data from DB
        mapping = self.repo.get_mapping_by_key(short_key=short_key)
        if not mapping:
            raise NotFoundError(f"No mapping for key '{short_key}'")

        # 2 check expiry
        if mapping.expires_at:
            expires_at = mapping.expires_at
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=ZoneInfo("UTC"))
            else:
                expires_at = expires_at.astimezone(ZoneInfo("UTC"))
            now = datetime.now(tz=ZoneInfo("UTC"))
            if expires_at < now:
                raise GoneError(f"Mapping for '{short_key}' expired at {mapping.expires_at.isoformat()}")

        # 3) All good
        return mapping.long_url
