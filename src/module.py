from src.config import DatabaseConfig
from src.dao.cipher_info_dao import CipherInfoDao
from src.dao.sqlite_impl.cipher_info_dao_sqlite_impl import CipherInfoDaoSqliteImpl
from src.dao.sqlite_impl.sqlite_client import SqliteClient
from src.features.ftp_supplier import FtpSupplier
from src.features.logging_supplier import get_logger

ftp_supplier = FtpSupplier()
sqlite_client = SqliteClient(DatabaseConfig.db_path)
cipher_info_dao: CipherInfoDao = CipherInfoDaoSqliteImpl(sqlite_client)
logger = get_logger("werkzeug")
