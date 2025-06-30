import pytest
from datetime import datetime, timedelta, timezone
from model.url_mapping import URLMapping
from mongoengine import connect, disconnect

@ pytest.fixture(autouse=True)
def db_connection():
    # Connect once per module
    disconnect(alias="default")
    connect(db="url_shortener_test", host="localhost", port=27017, alias="default")
    yield
    # Teardown: drop and disconnect
    URLMapping.drop_collection()
    disconnect(alias="default")


def test_save_invalid_expires():
    # expires before created should raise
    created = datetime.now(timezone.utc)
    expires = created - timedelta(hours=1)
    mapping = URLMapping(
        short_key="abc123",
        long_url="http://example.com",
        created_at=created,
        expires_at=expires
    )
    with pytest.raises(ValueError):
        mapping.save()


def test_is_expired_true_false():
    now = datetime.now(timezone.utc)
    past = now - timedelta(days=1)
    future = now + timedelta(days=1)

    m1 = URLMapping(short_key="past", long_url="x", created_at=now, expires_at=past)
    assert m1.is_expired() is True

    m2 = URLMapping(short_key="future", long_url="x", created_at=now, expires_at=future)
    assert m2.is_expired() is False

    m3 = URLMapping(short_key="none", long_url="x", created_at=now, expires_at=None)
    assert m3.is_expired() is False