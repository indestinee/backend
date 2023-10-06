from sqlite_dao_ext import SqliteClient, SqliteQuery

from src.client import UnifiedItem
from src.dao.unified_item_dao import UnifiedItemDao

sqlite_client = SqliteClient("/tmp/backend.db")
sqlite_client.execute(SqliteQuery("ALTER TABLE UnifiedItem RENAME TO UnifiedItemBak"))
unified_item_dao = UnifiedItemDao(sqlite_client)
unified_item_dao.create_table()
items = sqlite_client.execute(SqliteQuery("SELECT * FROM UnifiedItemBak"))[0]
items = [
    {
        **item,
        "is_encrypted": bool(int(item["is_encrypted"])),
    }
    for item in items
]
unified_item_dao.insert([UnifiedItem(**item) for item in items])
sqlite_client.execute(SqliteQuery("DROP TABLE UnifiedItemBak"))
