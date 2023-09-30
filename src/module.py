from src.config import DatabaseConfig
from src.dao.unified_item_dao import UnifiedItemDao
from src.dao.sqlite_impl.unified_item_dao_sqlite_impl import (
    UnifiedItemDaoSqliteImpl,
)
from src.dao.sqlite_impl.sqlite_client import SqliteClient
from src.features.unified_item_data_loader import UnifiedItemDataLoader
from src.features.cipher_supplier import CipherSupplier
from src.features.ftp_supplier import FtpSupplier
from src.features.logging_supplier import get_logger

sqlite_client = SqliteClient(DatabaseConfig.db_path)
cipher_supplier = CipherSupplier()
unified_item_dao: UnifiedItemDao = UnifiedItemDaoSqliteImpl(sqlite_client)

unified_item_data_loader = UnifiedItemDataLoader(unified_item_dao, cipher_supplier)
ftp_supplier = FtpSupplier(cipher_supplier)
logger = get_logger("werkzeug")
