from sqlite_dao_ext import SqliteClient

from src.config import ServerConfig
from src.dao.book_store_data_loader import BookStoreDataLoader
from src.features.cipher_supplier import CipherSupplier
from src.features.ftp_supplier import FtpSupplier
from src.features.logging_supplier import get_logger
from src.dao.unified_item_data_loader import UnifiedItemDataLoader

config = ServerConfig()
sqlite_client = SqliteClient(config.db_path)
cipher_supplier = CipherSupplier()

unified_item_data_loader = UnifiedItemDataLoader(sqlite_client, cipher_supplier)
book_store_data_loader = BookStoreDataLoader(sqlite_client)

ftp_supplier = FtpSupplier(cipher_supplier)
logger = get_logger("werkzeug")
