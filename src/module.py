from sqlite_dao_ext import SqliteClient

from src.config import ServerConfig
from src.dao.unified_item_dao import UnifiedItemDao
from src.data.unified_item import UnifiedItem
from src.features.unified_item_data_loader import UnifiedItemDataLoader
from src.features.cipher_supplier import CipherSupplier
from src.features.ftp_supplier import FtpSupplier
from src.features.logging_supplier import get_logger

config = ServerConfig()
sqlite_client = SqliteClient(config.db_path)
cipher_supplier = CipherSupplier()
unified_item_dao = UnifiedItemDao(sqlite_client)
unified_item_data_loader = UnifiedItemDataLoader(unified_item_dao, cipher_supplier)
ftp_supplier = FtpSupplier(cipher_supplier)
logger = get_logger("werkzeug")
