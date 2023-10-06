import dataclasses
import io
import os
from typing import List
from typing import Optional

import requests
from sqlite_dao_ext import SqliteDataObject


@dataclasses.dataclass(init=False)
class UnifiedItem(SqliteDataObject):
    source: str
    cipher_identifier: str
    name: str

    data: str
    is_encrypted: bool
    note: str = None

    @classmethod
    def primary_keys(cls) -> List[str]:
        return ["source", "cipher_identifier", "name"]


class Client:
    url: str
    sess: requests.Session

    def __init__(self, url: str, sess: requests.Session = None):
        self.url = url
        self.sess = sess if sess else requests.Session()

    def home(self):
        return self.get("/").text

    def ftp_list_dir(self, dir_path: str):
        return self.get("/flask/ftp/list_dir", dir_path=dir_path).json()

    def ftp_create_folder(self, dir_path: str):
        return self.post("/flask/ftp/create_folder", dir_path=dir_path).json()

    def ftp_upload(
        self,
        file_path: str,
        override: bool,
        file_data: bytes = None,
        local_file_path: str = None,
    ):
        if file_data is not None:
            fp = io.BytesIO(file_data)
        elif local_file_path is not None:
            fp = open(local_file_path, "rb")
        else:
            raise RuntimeError("file_data and local_file_path are both none")
        return self.sess.post(
            self._build_url_path("/flask/ftp/upload"),
            data={"file_path": file_path, "override": override},
            files=[("file", (os.path.basename(file_path), fp, "text/plain"))],
        ).json()

    def ftp_download(self, file_path: str, password: Optional[str] = None):
        return self.get("/flask/ftp/download", file_path=file_path, password=password)

    def ftp_delete(self, path: str):
        return self.delete("/flask/ftp/delete", path=path).json()

    def item_get(
        self,
        source: str,
        cipher_identifier: Optional[str] = None,
        name: Optional[str] = None,
        password: Optional[str] = None,
    ) -> List[UnifiedItem]:
        return [
            UnifiedItem.loads(item)
            for item in self.get(
                "/flask/item/get",
                source=source,
                cipher_identifier=cipher_identifier,
                name=name,
                password=password,
            ).json()["items"]
        ]

    def item_insert(self, items: List[UnifiedItem]):
        return self.post(
            "/flask/item/insert", items=[item.dumps() for item in items]
        ).json()

    def item_delete(
        self, source: str, cipher_identifier: str, name: Optional[str] = None
    ):
        return self.delete(
            "/flask/item/delete",
            source=source,
            cipher_identifier=cipher_identifier,
            name=name,
        ).json()

    def get(self, url_path: str, **params):
        return self.sess.get(self._build_url_path(url_path), params=params)

    def post(self, url_path: str, **params):
        return self.sess.post(self._build_url_path(url_path), json=params)

    def delete(self, url_path: str, **params):
        return self.sess.delete(self._build_url_path(url_path), json=params)

    def _build_url_path(self, url_path: str):
        return self.url.rstrip("/") + "/" + url_path.lstrip("/")
