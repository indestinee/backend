import logging
import threading
import time
import unittest

from src.client import Client, UnifiedItem, Book, Chapter, Media
from src.flaskr.server import create_app

logging.getLogger().setLevel(logging.DEBUG)


class IntegrationTest(unittest.TestCase):
    client: Client
    host = "127.0.0.1"
    port = 23333

    threading.Thread(
        target=create_app().run,
        kwargs={"host": host, "port": port, "debug": False},
        daemon=True,
    ).start()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = Client(f"http://{self.host}:{self.port}/")
        self.client.ftp_delete("test")

    def __del__(self):
        result = self.client.ftp_delete("test")
        logging.info("init delete result %s", result)
        print("init delete result")

    def test_home(self):
        self.assertEqual(self.client.home(), "Hello, World!")

    def test_404(self):
        self.assertEqual(self.client.get("/not_a_valid_url").status_code, 404)

    def test_ftp_folder(self):
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

    def test_ftp_file(self):
        self.assertTrue(self.client.ftp_create_folder("test/test_file")["success"])
        self.assertEqual(self.client.ftp_list_dir("test/test_file")["dirs"], [])

        self.assertTrue(
            self.client.ftp_upload("test/test_file/a.txt", file_data=b"hello")[
                "success"
            ]
        )
        self.assertFalse(
            self.client.ftp_upload("test/test_file/a.txt", file_data=b"world")[
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
        self.assertTrue(time.time() - 3600 < apple.created_at < time.time())
        self.assertTrue(time.time() - 3600 < apple.updated_at < time.time())

    def test_book_store(self):
        self.assertTrue(
            self.client.book_store_create_books(
                [
                    Book("test_source", f"test_identifier{i}", "url123", "title123")
                    for i in range(5)
                ]
            )["success"]
        )
        self.assertTrue(
            self.client.book_store_create_books(
                [
                    Book("test_source", f"test_identifier{i}", "url125", "title123")
                    for i in range(5)
                ]
            )["success"]
        )

        self.assertTrue(
            self.client.book_store_create_chapters(
                [
                    Chapter(
                        book_source="test_source",
                        book_identifier=f"test_identifier{i}",
                        chapter_identifier=f"c{idx}",
                        url=f"url{idx}",
                        title=f"title{idx}_{i}",
                        content=[
                            Media(text=f"{j}", image_url="123", image_base64="1234")
                            for j in range(100)
                        ],
                    )
                    for idx in range(10)
                    for i in range(2)
                ]
            )
        )
        books = self.client.book_store_get_books()
        logging.info("books: %s", books)
        self.assertEqual(len(books), 5)
        self.assertEqual(books[1].url, "url125")
        self.assertEqual(books[1].count_chapters, 10)
        catalogue = self.client.book_store_get_catalogue(
            "test_source", "test_identifier1"
        )
        logging.info("catalogue: %s", catalogue)
        self.assertEqual(len(catalogue.catalogue_items), 10)

        chapter = self.client.book_store_get_chapter(
            "test_source", "test_identifier1", "c0"
        )
        self.assertEqual(len(chapter.content), 100)
        self.assertEqual(
            chapter.content[0], Media(text="0", image_url="123", image_base64="1234")
        )

        self.assertTrue(
            self.client.book_store_delete_books("test_source", f"test_identifier1")[
                "success"
            ]
        )
        self.assertEqual(len(self.client.book_store_get_books()), 4)
        self.assertRaises(
            KeyError,
            lambda: self.client.book_store_get_catalogue(
                "test_source", "test_identifier1"
            ),
        )
        self.assertRaises(
            KeyError,
            lambda: self.client.book_store_get_chapter(
                "test_source", "test_identifier1", "c0"
            ),
        )
