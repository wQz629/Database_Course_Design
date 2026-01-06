import logging
import os
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

# 1. 确定项目根目录和日志目录
# 确保无论在哪里运行，日志都会放进项目根目录的 logs 文件夹里
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG_DIR = os.path.join(BASE_DIR, "logs")

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# 2. 配置日志格式
log_format = logging.Formatter('%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s')

# 3. 创建日志对象
logger = logging.getLogger("PharmacyMS")
logger.setLevel(logging.DEBUG)

# --- 控制台输出  ---
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_format)
logger.addHandler(console_handler)

# --- 每天自动生成一个新文件 (TimedRotatingFileHandler) ---
# filename: 日志基础名
# when: "midnight" 表示每天午夜切换
# interval: 1 表示每 1 天换一个文件
# backupCount: 30 表示只保留最近 30 天的日志，旧的会自动删除
app_log_path = os.path.join(LOG_DIR, "app.log")
file_handler = TimedRotatingFileHandler(
    app_log_path, 
    when="midnight", 
    interval=1, 
    backupCount=30, 
    encoding='utf-8'
)
file_handler.setFormatter(log_format)
logger.addHandler(file_handler)

# --- 专门把错误日志(ERROR/CRITICAL)单独存一个文件 ---
# 查 Bug 的时候不需要在几千行正常日志里翻，直接看 error.log 即可
error_log_path = os.path.join(LOG_DIR, "error.log")
error_handler = logging.FileHandler(error_log_path, encoding='utf-8')
error_handler.setLevel(logging.ERROR) # 只有 ERROR 及以上的才进这个文件
error_handler.setFormatter(log_format)
logger.addHandler(error_handler)