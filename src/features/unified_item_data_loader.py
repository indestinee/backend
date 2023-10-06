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
        items = self.dao.query_by_values(source=source, cipher_identifier=cipher_identifier, name=name)
        if key is None:
            return items
        return list(map(self.decrypt_item, items, [key] * len(items)))

    def decrypt_item(self, item: UnifiedItem, key: str) -> UnifiedItem:
        try:
            data = self.cipher_supplier.decrypt(key, item.data)
            new_item = UnifiedItem.loads(dataclasses.asdict(item))
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
