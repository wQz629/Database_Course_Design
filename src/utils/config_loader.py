import configparser
import os

def get_db_config():
    # 获取 config.ini 的绝对路径
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.ini')
    
    config = configparser.ConfigParser()
    config.read(config_path, encoding='utf-8')
    
    # 读取 database 这一节的内容
    db_info = {
        "host": config.get('database', 'host'),
        "port": config.getint('database', 'port'),  # 注意这里可以用 getint 转为整数
        "user": config.get('database', 'user'),
        "password": config.get('database', 'password'),
        "database": config.get('database', 'database'),
        "charset": config.get('database', 'charset')
    }
    return db_info

# 测试一下
if __name__ == "__main__":
    conf = get_db_config()
    print(f"准备连接到数据库: {conf['database']}，用户: {conf['user']}")