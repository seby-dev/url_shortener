import pytest
from datetime import datetime, timezone, timedelta
from repository.db_repo import DBRepository
from model.url_mapping import URLMapping
from mongoengine import connect, disconnect

@pytest.fixture(scope="module", autouse=True)
def db_connection():
    # Connect once per module
    disconnect(alias="default")
    connect(db="url_shortener_test", host="localhost", port=27017, alias="default")
    yield
    # Teardown: drop and disconnect
    URLMapping.drop_collection()
    disconnect(alias="default")

@pytest.fixture
def repo():
    return DBRepository()


def test_save_new_mapping(repo):
    now = datetime.now(timezone.utc)
    mapping = URLMapping(
        short_key="savekey",
        long_url="http://example.com/save",
        created_at=now,
        expires_at=None
    )
    saved = repo.save_url_mapping(mapping)
    assert hasattr(saved, 'short_key')
    assert saved.short_key == "savekey"
    # Verify persistence
    fetched = URLMapping.objects.get(short_key="savekey")
    assert fetched.long_url == "http://example.com/save"


def test_get_nonexistent_mapping(repo):
    assert repo.get_mapping_by_key("doesnotexist") is None


def test_get_existing_mapping(repo):
    now = datetime.now(timezone.utc)
    mapping = URLMapping(
        short_key="getkey",
        long_url="http://example.com/get",
        created_at=now
    )
    mapping.save()
    fetched = repo.get_mapping_by_key("getkey")
    assert fetched is not None
    assert fetched.long_url == "http://example.com/get"


def test_delete_mapping_success(repo):
    now = datetime.now(timezone.utc)
    mapping = URLMapping(
        short_key="delkey",
        long_url="http://example.com/delete",
        created_at=now
    )
    mapping.save()
    deleted = repo.delete_mapping("delkey")
    assert deleted is True
    assert repo.get_mapping_by_key("delkey") is None


def test_delete_mapping_failure(repo):
    # Try deleting again
    assert repo.delete_mapping("delkey") is False


def test_list_expired_mappings(repo):
    now = datetime.now(timezone.utc)
    expired = URLMapping(
        short_key="expired1",
        long_url="x",
        created_at=now - timedelta(days=2),
        expires_at=now - timedelta(days=1)
    )
    valid = URLMapping(
        short_key="valid1",
        long_url="x",
        created_at=now - timedelta(hours=1),
        expires_at=now + timedelta(hours=1)
    )
    expired.save()
    valid.save()

    expired_list = repo.list_expired_mappings()
    keys = {m.short_key for m in expired_list}
    assert "expired1" in keys
    assert "valid1" not in keys