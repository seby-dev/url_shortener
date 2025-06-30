from typing import Optional
from mongoengine import connect, DoesNotExist, ValidationError
from model.url_mapping import URLMapping
from model.url_mapping import current_time

# Establish MongoDB connection
connect(
    db="url_shortener",
    host="localhost",
    port=27017,
    username=None,
    password=None,
    authentication_source="admin"
)

class DBRepository:
    """
    Repository for CRUD operations on URLMapping documents
    """

    def save_url_mapping(self, mapping: URLMapping) -> URLMapping:
        """
        Save a new URLMapping or update an existing one
        :param mapping:
        :return: URLMapping
        """
        mapping.save()
        return mapping


    def get_mapping_by_key(self, short_key: str) -> Optional[URLMapping]:
        """
        Retrieve a URLMapping by its short_key.
        :param short_key:
        :return: returns None if not found
        """
        try:
            return URLMapping.objects.get(short_key=short_key)
        except (DoesNotExist, ValidationError):
            return None


    def delete_mapping(self, short_key: str) -> bool:
        """
        Delete a URLMapping by its short_key
        :param short_key:
        :return: True if a document was deleted, else False
        """
        result = URLMapping.objects(short_key=short_key).delete()
        return result > 0


    def list_expired_mappings(self) -> list[URLMapping]:
        """
        List all mappings that have expired (expires < now)
        :return: list of URLMappings
        """
        return list(URLMapping.objects(expires_at__lt=current_time()))











