from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QLineEdit, QLabel, 
                             QHeaderView, QMessageBox, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from src.controllers.inventory_ctrl import InventoryController

class InventoryPage(QWidget):
    def __init__(self):
        super().__init__()
        self.ctrl = InventoryController()
        self.init_ui()

    def init_ui(self):
        # 主布局
        layout = QVBoxLayout(self)

        # 1. 顶部工具栏（搜索区域）
        tool_frame = QFrame()
        tool_layout = QHBoxLayout(tool_frame)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入药品ID进行精确查询...")
        self.search_input.setFixedWidth(250)
        
        self.btn_search = QPushButton("查询库存")
        self.btn_search.clicked.connect(self.search_stock)
        
        self.btn_refresh = QPushButton("显示全部库存")
        self.btn_refresh.clicked.connect(self.load_all_data)
        
        tool_layout.addWidget(QLabel("药品筛选："))
        tool_layout.addWidget(self.search_input)
        tool_layout.addWidget(self.btn_search)
        tool_layout.addWidget(self.btn_refresh)
        tool_layout.addStretch()
        
        # 2. 表格区域
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["药品ID", "药品名称", "规格", "生产厂家", "库存总量", "有效期至"])
        
        # 设置布局策略：自适应内容 + 最后一列拉伸
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setStretchLastSection(True)
        
        # 3. 底部状态统计
        self.status_label = QLabel("当前库存状态：正在加载...")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")

        layout.addWidget(tool_frame)
        layout.addWidget(self.table)
        layout.addWidget(self.status_label)

        # 初始加载数据
        self.load_all_data()

    def fill_table_data(self, data_list):
        """通用表格填充逻辑"""
        self.table.setRowCount(0)
        if not data_list:
            self.status_label.setText("未发现库存记录。")
            return

        self.table.setRowCount(len(data_list))
        low_stock_count = 0
        
        for row_idx, row_data in enumerate(data_list):
            # 提取数据
            m_id = str(row_data['medicine_id'])
            m_name = str(row_data['medicine_name'])
            spec = str(row_data['specification'])
            manu = str(row_data['manufacturer'])
            stock = row_data['stock_quantity']
            expiry = str(row_data['expiry_date'])

            # 填充 Item
            self.table.setItem(row_idx, 0, QTableWidgetItem(m_id))
            self.table.setItem(row_idx, 1, QTableWidgetItem(m_name))
            self.table.setItem(row_idx, 2, QTableWidgetItem(spec))
            self.table.setItem(row_idx, 3, QTableWidgetItem(manu))
            
            # 库存数量项（带预警颜色）
            stock_item = QTableWidgetItem(str(stock))
            stock_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if stock < 10: # 低库存预警
                stock_item.setForeground(QColor("red"))
                font = QFont()
                font.setBold(True)
                stock_item.setFont(font)
                low_stock_count += 1
            self.table.setItem(row_idx, 4, stock_item)
            
            self.table.setItem(row_idx, 5, QTableWidgetItem(expiry))

        self.status_label.setText(f"总计 {len(data_list)} 种药品，其中 {low_stock_count} 种库存不足（红色标记）。")

    def load_all_data(self):
        """调用 Controller 获取全量库存"""
        success, res = self.ctrl.get_full_report()
        if success:
            self.fill_table_data(res)
        else:
            QMessageBox.critical(self, "错误", f"无法加载库存数据: {res}")

    def search_stock(self):
        """按 ID 查询单个库存"""
        m_id = self.search_input.text().strip()
        if not m_id:
            self.load_all_data()
            return

        success, res = self.ctrl.fetch_stock_by_id(m_id)
        if success:
            # 搜索结果通常只有一条，我们把它包装成列表复用 fill_table_data
            self.fill_table_data([res])
        else:
            # 如果没搜到，清空表格并提示
            self.table.setRowCount(0)
            self.status_label.setText(f"搜索结果：{res}")