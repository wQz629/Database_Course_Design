import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QListWidget, QStackedWidget, QLabel, QPushButton, 
                             QFrame, QStatusBar)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon

# 导入各个功能模块页面 
from src.ui.modules.base_info import BaseInfoPage
from src.ui.modules.purchase import PurchasePage
from src.ui.modules.inventory import InventoryPage
from src.ui.modules.sales import SalesPage
from src.ui.modules.statistics import StatisticsPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("医药销售管理系统 v1.0")
        self.resize(1200, 800)
        
        # 初始化界面
        self.init_ui()
        
    def init_ui(self):
        # 1. 主窗口的中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 2. 全局水平布局 (左侧导航 + 右侧内容)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- 左侧导航栏区域 ---
        sidebar = QFrame()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #2C3E50;
                border-right: 1px solid #1A252F;
            }
            QLabel {
                color: white;
                padding: 20px;
                font-size: 18px;
                font-weight: bold;
            }
            QListWidget {
                background-color: transparent;
                border: none;
                outline: none;
            }
            QListWidget::item {
                color: #BDC3C7;
                padding: 15px;
                font-size: 14px;
            }
            QListWidget::item:selected {
                background-color: #34495E;
                color: #3498DB;
                border-left: 5px solid #3498DB;
            }
            QListWidget::item:hover {
                background-color: #3E5871;
            }
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        
        # 系统 Logo / 标题
        logo_label = QLabel("医药管理系统")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(logo_label)

        # 导航列表
        self.nav_list = QListWidget()
        self.nav_list.addItem("基础信息管理")
        self.nav_list.addItem("进货管理")
        self.nav_list.addItem("库房管理")
        self.nav_list.addItem("销售管理")
        self.nav_list.addItem("财务统计")
        self.nav_list.addItem("系统维护")
        
        # 默认选中第一项
        self.nav_list.setCurrentRow(0)
        self.nav_list.currentRowChanged.connect(self.switch_page)
        sidebar_layout.addWidget(self.nav_list)
        sidebar_layout.addStretch() # 底部留白

        # --- 右侧内容区域 ---
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(10, 10, 10, 10)

        # 页标题栏
        self.page_title = QLabel("基础信息管理")
        self.page_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #333; margin-bottom: 10px;")
        content_layout.addWidget(self.page_title)

        # 堆栈窗口 (核心容器)
        self.stack = QStackedWidget()
        
        # 实例化各个页面并加入堆栈
        self.page_base_info = BaseInfoPage()
        self.page_purchase = PurchasePage()
        self.page_inventory = InventoryPage()
        self.page_sales = SalesPage()
        self.page_stats = StatisticsPage()
        self.page_system = QWidget() # 暂时占位

        self.stack.addWidget(self.page_base_info) # Index 0
        self.stack.addWidget(self.page_purchase)  # Index 1
        self.stack.addWidget(self.page_inventory) # Index 2
        self.stack.addWidget(self.page_sales)     # Index 3
        self.stack.addWidget(self.page_stats)     # Index 4
        self.stack.addWidget(self.page_system)    # Index 5

        content_layout.addWidget(self.stack)

        # 将左右两部分加入主布局
        main_layout.addWidget(sidebar)
        main_layout.addWidget(content_container)

        # 状态栏
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("系统就绪 | 当前操作员：Admin")

    def switch_page(self, index):
        """切换导航项时触发"""
        self.stack.setCurrentIndex(index)
        # 更新页面标题
        nav_text = self.nav_list.currentItem().text()
        self.page_title.setText(nav_text)