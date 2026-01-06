import sys
import traceback
from PyQt6.QtWidgets import QApplication, QMessageBox
from src.ui.main_window import MainWindow
from src.utils.logger import logger  

def global_exception_handler(exc_type, exc_value, exc_traceback):
    """
    全局异常捕获函数：当程序发生未处理的崩溃时，记录日志并弹窗，防止无声无息的闪退。
    """
    # 如果是键盘中断（Ctrl+C），忽略
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    # 将错误堆栈转换为字符串
    err_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    
    # 记录到日志文件（CRITICAL 级别）
    logger.critical(f"检测到未捕获的系统崩溃:\n{err_msg}")

    # 给用户一个友好的弹窗提示
    error_dialog = QMessageBox()
    error_dialog.setIcon(QMessageBox.Icon.Critical)
    error_dialog.setWindowTitle("系统崩溃")
    error_dialog.setText("抱歉，程序发生了严重错误并即将关闭。")
    error_dialog.setInformativeText("错误详情已记录至日志文件，请联系开发人员。")
    error_dialog.setDetailedText(err_msg)
    error_dialog.exec()

    # 确保程序安全退出
    sys.exit(1)

def main():
    # 1. 设置系统全局异常钩子
    sys.excepthook = global_exception_handler

    logger.info("==========================================")
    logger.info("医药销售管理系统 v1.0 正在启动...")
    
    try:
        app = QApplication(sys.argv)
        
        app.setStyle("Fusion") 
        logger.debug("已设置 UI 样式为 Fusion")

        window = MainWindow()
        window.show()
        logger.info("主窗口显示成功，进入事件循环。")
        
        exit_code = app.exec()
        
        logger.info(f"程序正常关闭，退出代码: {exit_code}")
        sys.exit(exit_code)

    except Exception as e:
        # 捕获启动阶段可能发生的异常（如数据库连接配置错误）
        logger.error(f"启动阶段发生异常: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()