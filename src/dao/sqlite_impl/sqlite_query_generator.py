import dataclasses
import json
import time
from typing import List, Any

from src.dao.sqlite_impl.sqlite_client import SqliteQuery


class SqliteQueryGenerator:
    @classmethod
    def create_sql(
        cls,
        table_name: str,
        clz: dataclasses.dataclass,
        primary_keys: List[str] = None,
    ) -> SqliteQuery:
        db_columns = cls._build_db_columns(clz, primary_keys)
        primary_keys = (
            [f"PRIMARY KEY ({', '.join(primary_keys)})"] if primary_keys else []
        )
        return SqliteQuery(
            f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(db_columns + primary_keys)});"
        )

    @classmethod
    def _build_db_columns(
        cls, clz: dataclasses.dataclass, primary_keys: List[str]
    ) -> List[str]:
        return [
            # pylint: disable-next=line-too-long
            f"{field.name} {cls._determine_db_type(field)}{' NOT NULL' if primary_keys and field.name in primary_keys else ''}"
            for field in dataclasses.fields(clz)
        ]

    @classmethod
    def _determine_db_type(cls, field: dataclasses.Field) -> str:
        if field.name.endswith("_at"):
            return "TIMESTAMP"
        if field.type is int:
            return "INTEGER"
        if field.type is float:
            return "REAL"
        if field.type is Any:
            return "BLOB"
        return "TEXT"

    @classmethod
    def create_insert_or_replace(
        cls,
        table_name: str,
        clz: dataclasses.dataclass,
        objs: List[dataclasses.dataclass],
    ) -> SqliteQuery:
        fields = {field.name: field for field in dataclasses.fields(clz)}
        keys = [field.name for field in dataclasses.fields(clz)]
        return SqliteQuery(
            # pylint: disable-next=line-too-long
            f"INSERT OR REPLACE INTO {table_name} ({', '.join(keys)}) VALUES ({', '.join('?' * len(keys))})",
            *[
                [
                    cls._serialize(cls._determine_value(obj.__dict__[key], fields[key]))
                    for key in keys
                ]
                for obj in objs
            ],
        )

    @classmethod
    def _determine_value(cls, value: Any, field: dataclasses.Field) -> Any:
        if field.type is float and field.name == "updated_at":
            return time.time()
        if value is not None:
            return value
        if field.default_factory and field.default_factory != dataclasses.MISSING:
            return field.default_factory()
        if field.default and field.default != dataclasses.MISSING:
            return field.default
        if field.type is float and field.name == "created_at":
            return time.time()
        return None

    @classmethod
    def _serialize(cls, value: Any):
        if isinstance(value, (int, str, float)):
            return value
        if isinstance(value, (list, dict)):
            return json.dumps(value)
        if dataclasses.is_dataclass(value):
            return json.dumps(dataclasses.asdict(value))
        return value
