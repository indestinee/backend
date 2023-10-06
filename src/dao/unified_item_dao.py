from sqlite_dao_ext import SqliteDao, SqliteClient

from src.data.unified_item import UnifiedItem


class UnifiedItemDao(SqliteDao[UnifiedItem]):
    def __init__(self, sqlite_client: SqliteClient):
        super().__init__(sqlite_client, UnifiedItem)
