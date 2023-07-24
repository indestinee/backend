import dataclasses


@dataclasses.dataclass
class CipherInfo:
    source: str
    cipher_identifier: str
    name: str

    data: str
    note: str = None

    created_at: float = None
    updated_at: float = None
