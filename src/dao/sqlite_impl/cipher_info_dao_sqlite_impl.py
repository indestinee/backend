from typing import List

from src.dao.cipher_info_dao import CipherInfoDao
from src.dao.sqlite_impl.sqlite_client import SqliteClient, SqliteQuery
from src.dao.sqlite_impl.sqlite_query_generator import SqliteQueryGenerator
from src.data.cipher_info import CipherInfo


class CipherInfoDaoSqliteImpl(CipherInfoDao):
    _sqlite_client: SqliteClient
    table_name: str = CipherInfo.__name__

    def __init__(self, sqlite_client: SqliteClient):
        self._sqlite_client = sqlite_client
        self._create_table()

    def _create_table(self):
        sql = SqliteQueryGenerator.create_sql(
            self.table_name,
            CipherInfo,
            primary_keys=["source", "cipher_identifier", "name"],
        )
        self._sqlite_client.execute(sql)

    def query_by_identifier(
        self, source: str, cipher_identifier: str
    ) -> List[CipherInfo]:
        sql = SqliteQuery(
            f"""SELECT * FROM {self.table_name} WHERE cipher_identifier = ? AND source = ?""",
            cipher_identifier,
            source,
        )
        return [
            CipherInfo(**row) for row in self._sqlite_client.execute(sql, dump=False)[0]
        ]

    def insert_or_replace(self, cipher_infos: List[CipherInfo]):
        sql = SqliteQueryGenerator.create_insert_or_replace(
            self.table_name, CipherInfo, cipher_infos
        )
        self._sqlite_client.batch_insert(sql)

    def delete_by_identifier_and_names(
        self, source: str, cipher_identifier: str, names: List[str] = None
    ):
        if names:
            self._sqlite_client.execute(
                SqliteQuery(
                    f"DELETE FROM {self.table_name} WHERE source = ? AND cipher_identifier = ? AND name IN ({', '.join('?' * len(names))})",
                    source,
                    cipher_identifier,
                    *names,
                )
            )
        elif names is None:
            self._sqlite_client.execute(
                SqliteQuery(
                    f"DELETE FROM {self.table_name} WHERE source = ? AND cipher_identifier = ?",
                    source,
                    cipher_identifier,
                )
            )
