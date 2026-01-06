# src/utils/logger.py
import logging
import os
from datetime import datetime

# 1. 确定日志存放路径（存放在项目根目录下的 logs 文件夹）
# 路径逻辑：src/utils/logger.py -> src/utils -> src -> 根目录 -> logs
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG_DIR = os.path.join(BASE_DIR, "logs")

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# 2. 生成以日期命名的日志文件名 (例如: 2026-01-06.log)
log_filename = datetime.now().strftime("%Y-%m-%d") + ".log"
log_path = os.path.join(LOG_DIR, log_filename)

# 3. 配置日志格式
# 格式：时间 - 日志级别 - [文件名:行号] - 消息内容
log_format = logging.Formatter('%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s')

# 4. 创建日志对象
logger = logging.getLogger("PharmacyMS")
logger.setLevel(logging.DEBUG)  # 设置记录级别为 DEBUG (记录最详细的信息)

# 5. 创建文件处理器 (用于写入文件)
file_handler = logging.FileHandler(log_path, encoding='utf-8')
file_handler.setFormatter(log_format)

# 6. 创建控制台处理器 (方便开发时在屏幕看)
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_format)

# 7. 添加处理器
logger.addHandler(file_handler)
logger.addHandler(console_handler)
