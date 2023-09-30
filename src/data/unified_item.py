import dataclasses


@dataclasses.dataclass
class UnifiedItem:
    source: str
    cipher_identifier: str
    name: str

    data: str
    note: str = None

    created_at: float = None
    updated_at: float = None

    @classmethod
    def from_json(cls, **kwargs):
        return UnifiedItem(**kwargs)
