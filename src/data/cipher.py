import dataclasses
import json


@dataclasses.dataclass
class Cipher:
    cipher_text: str
    text_length: int
    salt: str

    def dumps(self):
        return json.dumps(dataclasses.asdict(self))
