import dataclasses
from typing import List

from src.dao.unified_item_dao import UnifiedItemDao
from src.data.unified_item import UnifiedItem
from src.features.cipher_supplier import CipherSupplier
from src.features.exceptions import CheckedException


@dataclasses.dataclass
class UnifiedItemDataLoader:
    dao: UnifiedItemDao
    cipher_supplier: CipherSupplier

    def query_by_identifier(
        self,
        source: str,
        cipher_identifier: str,
        name: str = None,
        key: str = None,
    ) -> List[UnifiedItem]:
        items = (
            self.dao.query_by_identifier(source, cipher_identifier)
            if name is None
            else self.dao.query_by_name(source, cipher_identifier, name)
        )
        if key is None:
            return items
        return list(map(self.decrypt_item, items, [key] * len(items)))

    def decrypt_item(self, item: UnifiedItem, key: str) -> UnifiedItem:
        try:
            data = self.cipher_supplier.decrypt(key, item.data)
            new_item = UnifiedItem.from_json(**dataclasses.asdict(item))
            new_item.data = self.deserialize(data)
            return new_item
        except Exception as _:
            raise CheckedException("decrypt failed")

    @staticmethod
    def deserialize(data: bytes):
        try:
            return data.decode("utf-8")
        except:
            return data.hex()
