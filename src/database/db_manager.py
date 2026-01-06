import pymysql
import pymysql.cursors
from src.utils.config_loader import get_db_config 
from src.utils.logger import logger
from contextlib import contextmanager

class DBManager:
    _instance = None  # 用于存放单例

    def __new__(cls, *args, **kwargs):
        """单例模式：确保全局只有一个 DBManager 实例"""
        if not cls._instance:
            cls._instance = super(DBManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # 增加一个标识，确保 __init__ 里的逻辑（如读配置、打日志）只执行一次
        if not hasattr(self, '_initialized'):
            try:
                self.db_config = get_db_config()
                logger.debug("数据库连接配置读取成功（全局初始化）")
                self._initialized = True
            except Exception as e:
                logger.error(f"初始化DBManager失败: {e}")
                raise e

    @contextmanager
    def session(self):
        """上下文管理器代码保持不变..."""
        conn = None
        try:
            conn = pymysql.connect(
                host=self.db_config['host'],
                port=self.db_config['port'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                database=self.db_config['database'],
                charset=self.db_config['charset'],
                autocommit=True,
                connect_timeout=5
            )
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            yield cursor
        except Exception as e:
            logger.error(f"数据库会话异常: {e}")
            if conn: conn.rollback()
            raise e
        finally:
            if conn:
                cursor.close()
                conn.close()

    def execute_with_error_handle(self, func, *args, **kwargs):
        """保持不变..."""
        try:
            result = func(*args, **kwargs)
            return True, result
        except pymysql.MySQLError as e:
            error_msg = str(e.args[1]) if len(e.args) > 1 else str(e)
            logger.warning(f"触发器拦截: {error_msg}")
            return False, error_msg
        except Exception as e:
            logger.error(f"执行异常: {e}")
            return False, str(e)