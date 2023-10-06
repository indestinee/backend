import logging
import threading
import time
import unittest

from src.client import Client, UnifiedItem
from src.flaskr.server import create_app

logging.getLogger().setLevel(logging.DEBUG)


class IntegrationTest(unittest.TestCase):
    client: Client
    thread: threading.Thread

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        app = create_app()
        host, port = "127.0.0.1", 23333
        self.thread = threading.Thread(
            target=app.run, kwargs={"host": host, "port": port, "debug": False}
        )
        self.thread.daemon = True
        self.thread.start()
        time.sleep(1)
        self.client = Client(f"http://{host}:{port}/")
        result = self.client.ftp_delete("test")
        logging.info("init delete result %s", result)

    def __del__(self):
        result = self.client.ftp_delete("test")
        logging.info("init delete result %s", result)

    def test_home(self):
        self.assertEqual(self.client.home(), "Hello, World!")

    def test_404(self):
        self.assertEqual(self.client.get("/not_a_valid_url").status_code, 404)

    def test_ftp(self):
        self.assertTrue(self.client.ftp_create_folder("test/test_folder")["success"])
        self.assertEqual(self.client.ftp_list_dir("test/test_folder")["dirs"], [])

        self.assertTrue(self.client.ftp_create_folder("test/test_folder/a")["success"])
        self.assertTrue(self.client.ftp_create_folder("test/test_folder/b")["success"])
        self.assertEqual(
            {x["name"] for x in self.client.ftp_list_dir("test/test_folder")["dirs"]},
            {"a", "b"},
        )
        self.assertTrue(self.client.ftp_delete("test/test_folder/a")["success"])
        self.assertFalse(self.client.ftp_delete("test/test_folder/c")["success"])
        self.assertEqual(
            {x["name"] for x in self.client.ftp_list_dir("test/test_folder")["dirs"]},
            {"b"},
        )
        self.assertFalse(self.client.ftp_list_dir("../")["success"])

    def test_file(self):
        self.assertTrue(self.client.ftp_create_folder("test/test_file")["success"])
        self.assertEqual(self.client.ftp_list_dir("test/test_file")["dirs"], [])

        self.assertTrue(
            self.client.ftp_upload("test/test_file/a.txt", False, file_data=b"hello")[
                "success"
            ]
        )
        self.assertFalse(
            self.client.ftp_upload("test/test_file/a.txt", False, file_data=b"world")[
                "success"
            ]
        )
        self.assertEqual(
            self.client.ftp_list_dir("test/test_file")["dirs"][0]["name"], "a.txt"
        )

        self.assertFalse(self.client.ftp_download("../", None).json()["success"])
        self.assertEqual(
            self.client.ftp_download("test/test_file/a.txt", None).text, "hello"
        )

        self.assertTrue(
            self.client.ftp_upload("test/test_file/a.txt", True, file_data=b"world")[
                "success"
            ]
        )
        self.assertEqual(
            self.client.ftp_download("test/test_file/a.txt", None).text, "world"
        )

    def test_unified_item(self):
        for item in self.client.item_get("test"):
            self.assertTrue(
                self.client.item_delete(item.source, item.cipher_identifier, item.name)
            )
        items = self.client.item_get("test")
        self.assertEqual(len(items), 0)
        for name in ["apple", "banana"]:
            self.assertTrue(
                self.client.item_insert(
                    [
                        UnifiedItem(
                            source="test",
                            cipher_identifier="cipher",
                            name=name,
                            data=name + "_data",
                            is_encrypted=False,
                            note="hello",
                        )
                    ]
                )
            )
        items = self.client.item_get("test")
        logging.info("items: %s", items)
        self.assertEqual(len(items), 0)
        self.assertEqual(len(self.client.item_get("test", "cipher")), 2)
        self.assertEqual(len(self.client.item_get("test", "cipher", "apple")), 1)

        apple = self.client.item_get("test", "cipher", "apple")[0]
        self.assertEqual(apple.data, "apple_data")
        self.assertFalse(apple.is_encrypted)
        self.assertEqual(apple.note, "hello")
        self.assertTrue(
            apple.created_at > time.time() - 3600 and apple.created_at <= time.time()
        )
        self.assertTrue(
            apple.updated_at > time.time() - 3600 and apple.updated_at <= time.time()
        )
