import sys
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QLabel, QHeaderView, 
                             QTabWidget, QMessageBox, QGroupBox, QGridLayout, QComboBox)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor # 统一放在顶部
from src.controllers.finance_ctrl import FinanceController

class StatisticsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.f_ctrl = FinanceController()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        
        # 两个选项卡
        self.tab_daily = QWidget()
        self.tab_monthly = QWidget()
        
        self.init_daily_ui()
        self.init_monthly_ui()
        
        self.tabs.addTab(self.tab_daily, "日销售统计流水")
        self.tabs.addTab(self.tab_monthly, "月度经营报表")
        
        # 优化：切换到“日统计”标签时自动刷新数据
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        layout.addWidget(self.tabs)
        
        # 初始加载数据
        self.refresh_daily_table()

    def on_tab_changed(self, index):
        if index == 0: # 日统计页
            self.refresh_daily_table()

    # ---------------------------
    # 选项卡1：日统计流水
    # ---------------------------
    def init_daily_ui(self):
        layout = QVBoxLayout(self.tab_daily)
        
        tool_layout = QHBoxLayout()
        btn_refresh = QPushButton("刷新日结数据")
        btn_refresh.clicked.connect(self.refresh_daily_table)
        tool_layout.addWidget(btn_refresh)
        tool_layout.addStretch()
        layout.addLayout(tool_layout)
        
        self.daily_table = QTableWidget()
        self.daily_table.setColumnCount(5)
        self.daily_table.setHorizontalHeaderLabels(["统计日期", "当日销售额", "当日退货额", "当日净额", "销售单数"])
        
        header = self.daily_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.daily_table)

    def refresh_daily_table(self):
        """获取日汇总数据并渲染"""
        success, data = self.f_ctrl.get_daily_logs()
        if success:
            self.daily_table.setRowCount(0) # 先清空
            if not data: return
            
            self.daily_table.setRowCount(len(data))
            for row, d in enumerate(data):
                self.daily_table.setItem(row, 0, QTableWidgetItem(str(d['summary_date'])))
                self.daily_table.setItem(row, 1, QTableWidgetItem(f"￥{float(d['total_sales_amount']):.2f}"))
                self.daily_table.setItem(row, 2, QTableWidgetItem(f"￥{float(d['total_return_amount']):.2f}"))
                
                # 净利润着色：赚钱蓝色，亏钱红色
                net = float(d['net_amount'])
                net_item = QTableWidgetItem(f"￥{net:.2f}")
                if net < 0:
                    net_item.setForeground(QColor("red"))
                else:
                    net_item.setForeground(QColor("blue"))
                
                self.daily_table.setItem(row, 3, net_item)
                self.daily_table.setItem(row, 4, QTableWidgetItem(str(d['order_count'])))
        else:
            QMessageBox.warning(self, "查询失败", f"无法加载统计数据: {data}")

    # ---------------------------
    # 选项卡2：月度汇总报表
    # ---------------------------
    def init_monthly_ui(self):
        layout = QVBoxLayout(self.tab_monthly)
        
        filter_group = QGroupBox("月度报表筛选")
        filter_layout = QHBoxLayout(filter_group)
        
        self.combo_year = QComboBox()
        cur_y = QDate.currentDate().year()
        for y in range(cur_y - 5, cur_y + 1):
            self.combo_year.addItem(str(y))
        self.combo_year.setCurrentText(str(cur_y))
        
        self.combo_month = QComboBox()
        for m in range(1, 13):
            self.combo_month.addItem(str(m).zfill(2))
        self.combo_month.setCurrentText(str(QDate.currentDate().month()).zfill(2))
        
        btn_calc = QPushButton("执行月度统计")
        btn_calc.setStyleSheet("background-color: #2196F3; color: white; padding: 5px;")
        btn_calc.clicked.connect(self.calculate_monthly)
        
        filter_layout.addWidget(QLabel("年份:"))
        filter_layout.addWidget(self.combo_year)
        filter_layout.addWidget(QLabel("月份:"))
        filter_layout.addWidget(self.combo_month)
        filter_layout.addWidget(btn_calc)
        filter_layout.addStretch()
        
        res_group = QGroupBox("本月经营概况")
        grid = QGridLayout(res_group)
        
        val_font = QFont("Arial", 20, QFont.Weight.Bold)
        
        self.val_m_sales = QLabel("￥0.00")
        self.val_m_sales.setFont(val_font)
        self.val_m_sales.setStyleSheet("color: green;")
        
        self.val_m_return = QLabel("￥0.00")
        self.val_m_return.setFont(val_font)
        self.val_m_return.setStyleSheet("color: red;")
        
        self.val_m_net = QLabel("￥0.00")
        self.val_m_net.setFont(val_font)
        self.val_m_net.setStyleSheet("color: blue;")
        
        self.val_m_orders = QLabel("0")
        self.val_m_orders.setFont(val_font)
        
        grid.addWidget(QLabel("月销售总额:"), 0, 0)
        grid.addWidget(self.val_m_sales, 1, 0)
        grid.addWidget(QLabel("月退货总额:"), 0, 1)
        grid.addWidget(self.val_m_return, 1, 1)
        grid.addWidget(QLabel("月净利润额:"), 2, 0)
        grid.addWidget(self.val_m_net, 3, 0)
        grid.addWidget(QLabel("月订单总数:"), 2, 1)
        grid.addWidget(self.val_m_orders, 3, 1)

        layout.addWidget(filter_group)
        layout.addWidget(res_group)
        layout.addStretch()

    def calculate_monthly(self):
        year = self.combo_year.currentText()
        month = self.combo_month.currentText()
        
        success, data = self.f_ctrl.get_monthly_summary(year, month)
        
        if success:
            # 安全取值，防止 SQL 返回 None
            s = data.get('month_sales') or 0
            r = data.get('month_return') or 0
            n = data.get('month_net') or 0
            o = data.get('month_orders') or 0
            
            self.val_m_sales.setText(f"￥{float(s):.2f}")
            self.val_m_return.setText(f"￥{float(r):.2f}")
            self.val_m_net.setText(f"￥{float(n):.2f}")
            self.val_m_orders.setText(str(int(o)))
        else:
            QMessageBox.warning(self, "错误", f"统计失败: {data}")