import pymysql
import pymysql.cursors
from src.utils.config_loader import get_db_config 
from contextlib import contextmanager

class DBManager:
    def __init__(self):
        # 动态读取配置
        self.db_config = get_db_config()

    @contextmanager
    def session(self):
        """
        上下文管理器：自动管理连接和游标
        使用方法: with db.session() as cursor:
        """
        conn = pymysql.connect(
            host=self.db_config['host'],
            port=self.db_config['port'],
            user=self.db_config['user'],
            password=self.db_config['password'],
            database=self.db_config['database'],
            charset=self.db_config['charset'],
            autocommit=True  # 设为True，简单的单条操作自动提交
        )
        # 使用 DictCursor，查询结果将以字典形式返回，例如：{'medicine_name': '阿莫西林'}
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        try:
            yield cursor
        except Exception as e:
            conn.rollback() # 出错时回滚
            raise e
        finally:
            cursor.close()
            conn.close()

    def execute_with_error_handle(self, func, *args, **kwargs):
        """
        统一异常处理装饰器，用于捕获触发器抛出的 45000 错误
        """
        try:
            return True, func(*args, **kwargs)
        except pymysql.MySQLError as e:
            # 提取触发器 SIGNAL 抛出的错误消息
            error_msg = str(e.args[1]) if len(e.args) > 1 else str(e)
            return False, error_msg