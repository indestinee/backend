import abc
from typing import List

from src.data.cipher_info import CipherInfo


class CipherInfoDao(abc.ABC):
    @abc.abstractmethod
    def query_by_identifier(
        self, source: str, cipher_identifier: str
    ) -> List[CipherInfo]:
        ...

    @abc.abstractmethod
    def insert_or_replace(self, cipher_infos: List[CipherInfo]):
        ...

    @abc.abstractmethod
    def delete_by_identifier_and_names(
        self, source: str, cipher_identifier: str, names: List[str] = None
    ):
        ...
