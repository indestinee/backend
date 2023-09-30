import abc
from typing import List

from src.data.unified_item import UnifiedItem


class UnifiedItemDao(abc.ABC):
    @abc.abstractmethod
    def query_by_identifier(
        self, source: str, cipher_identifier: str
    ) -> List[UnifiedItem]:
        ...

    @abc.abstractmethod
    def query_by_name(
        self, source: str, cipher_identifier: str, name: str
    ) -> List[UnifiedItem]:
        ...

    @abc.abstractmethod
    def insert_or_replace(self, items: List[UnifiedItem]):
        ...

    @abc.abstractmethod
    def delete_by_identifier_and_names(
        self, source: str, cipher_identifier: str, names: List[str] = None
    ):
        ...
