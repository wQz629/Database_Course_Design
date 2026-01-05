# test_show_data.py
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTableWidget, 
                             QTableWidgetItem, QVBoxLayout, QWidget, QPushButton, QMessageBox)
from src.database.dao import CustomerDAO

class CustomerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("医药系统 - 客户信息查看")
        self.resize(800, 500)

        # 1. 布局初始化
        layout = QVBoxLayout()
        self.table = QTableWidget()
        self.btn_refresh = QPushButton("刷新数据")
        self.btn_refresh.clicked.connect(self.load_data)

        layout.addWidget(self.table)
        layout.addWidget(self.btn_refresh)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # 2. 初始加载
        self.load_data()

    def load_data(self):
        """调用 DAO 获取数据并渲染表格"""
        dao = CustomerDAO()
        success, data = dao.get_all_customers()

        if not success:
            QMessageBox.critical(self, "错误", f"无法获取数据: {data}")
            return

        # 设置表格行数和列数
        self.table.setRowCount(len(data))
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["客户ID", "姓名", "电话", "地址"])

        # 填入数据
        for row_index, row_data in enumerate(data):
            for col_index, value in enumerate(row_data):
                # QTableWidget 必须填入 QTableWidgetItem 对象
                item = QTableWidgetItem(str(value))
                self.table.setItem(row_index, col_index, item)
        
        # 自动调整列宽
        self.table.resizeColumnsToContents()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CustomerWindow()
    window.show()
    sys.exit(app.exec())