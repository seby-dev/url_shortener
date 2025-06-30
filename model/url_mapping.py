from datetime import datetime
from mongoengine import Document, StringField, DateTimeField


def current_time() -> datetime:
    """
    Returns the current time
    :return: datetime
    """
    return datetime.utcnow()


class URLMapping(Document):
    """
    A mapping from a short key to a long URL, with optional expiration
    """
    meta = {'collection': 'url_mappings'}
    short_key = StringField(primary_key=True, required=True)
    long_url = StringField(required=True)
    created_at = DateTimeField(default=current_time(), required=True)
    expires_at = DateTimeField(null=True)


    def save(self, *args, **kwargs):
        # Enforce expires_at >= created_at using timestamps to handle aware/naive mix
        if self.expires_at and self.created_at:
            try:
                if self.expires_at.timestamp() < self.created_at.timestamp():
                    raise ValueError("expires_at must not be before created_at")
            except Exception:
                # In unusual cases, fallback to direct comparison
                if self.expires_at < self.created_at:
                    raise ValueError("expires_at must not be before created_at")
        return super(URLMapping, self).save(*args, **kwargs)

    def is_expired(self) -> bool:
        """
        Returns True if this mapping has expired
        :return: bool
        """
        if not self.expires_at:
            return False
            # Compare using timestamps against current UTC
        return self.expires_at.timestamp() < datetime.utcnow().timestamp()


