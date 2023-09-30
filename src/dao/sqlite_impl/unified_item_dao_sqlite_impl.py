from typing import List

from src.dao.sqlite_impl.sqlite_client import SqliteClient, SqliteQuery
from src.dao.sqlite_impl.sqlite_query_generator import SqliteQueryGenerator
from src.dao.unified_item_dao import UnifiedItemDao
from src.data.unified_item import UnifiedItem


class UnifiedItemDaoSqliteImpl(UnifiedItemDao):
    _sqlite_client: SqliteClient
    table_name: str = UnifiedItem.__name__

    def __init__(self, sqlite_client: SqliteClient):
        self._sqlite_client = sqlite_client
        self._create_table()

    def _create_table(self):
        sql = SqliteQueryGenerator.create_sql(
            self.table_name,
            UnifiedItem,
            primary_keys=["source", "cipher_identifier", "name"],
        )
        self._sqlite_client.execute(sql)

    def query_by_identifier(
        self,
        source: str,
        cipher_identifier: str,
    ) -> List[UnifiedItem]:
        sql = SqliteQuery(
            # pylint: disable-next=line-too-long
            f"SELECT * FROM {self.table_name} WHERE source = ? AND cipher_identifier = ?",
            source,
            cipher_identifier,
        )
        return [
            UnifiedItem.from_json(**row)
            for row in self._sqlite_client.execute(sql, dump=False)[0]
        ]

    def query_by_name(
        self,
        source: str,
        cipher_identifier: str,
        name: str,
    ) -> List[UnifiedItem]:
        sql = SqliteQuery(
            # pylint: disable-next=line-too-long
            f"SELECT * FROM {self.table_name} WHERE source = ? AND cipher_identifier = ? AND name = ?",
            source,
            cipher_identifier,
            name,
        )
        return [
            UnifiedItem.from_json(**row)
            for row in self._sqlite_client.execute(sql, dump=False)[0]
        ]

    def insert_or_replace(self, items: List[UnifiedItem]):
        sql = SqliteQueryGenerator.create_insert_or_replace(
            self.table_name, UnifiedItem, items
        )
        self._sqlite_client.batch_insert(sql)

    def delete_by_identifier_and_names(
        self, source: str, cipher_identifier: str, names: List[str] = None
    ):
        if names:
            self._sqlite_client.execute(
                SqliteQuery(
                    # pylint: disable-next=line-too-long
                    f"DELETE FROM {self.table_name} WHERE source = ? AND cipher_identifier = ? AND name IN ({', '.join('?' * len(names))})",
                    source,
                    cipher_identifier,
                    *names,
                )
            )
        elif names is None:
            self._sqlite_client.execute(
                SqliteQuery(
                    # pylint: disable-next=line-too-long
                    f"DELETE FROM {self.table_name} WHERE source = ? AND cipher_identifier = ?",
                    source,
                    cipher_identifier,
                )
            )
