from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QLineEdit, QLabel, 
                             QHeaderView, QTabWidget, QMessageBox, QComboBox, 
                             QDoubleSpinBox, QSpinBox, QGroupBox, QFormLayout, QDialog)
from PyQt6.QtCore import Qt, QDateTime
from src.controllers.purchase_ctrl import PurchaseController
from src.controllers.base_info_ctrl import BaseInfoController

# ==========================================
# 辅助类：进货详情弹窗
# ==========================================
class PurchaseDetailDialog(QDialog):
    def __init__(self, order_id, items):
        super().__init__()
        self.setWindowTitle(f"单据详情 - {order_id}")
        self.resize(600, 400)
        layout = QVBoxLayout(self)
        
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["药品ID", "药品名称", "规格", "入库数量", "采购单价"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        table.setRowCount(len(items))
        for row, item in enumerate(items):
            table.setItem(row, 0, QTableWidgetItem(str(item['medicine_id'])))
            table.setItem(row, 1, QTableWidgetItem(str(item['medicine_name'])))
            table.setItem(row, 2, QTableWidgetItem(str(item['specification'])))
            table.setItem(row, 3, QTableWidgetItem(str(item['quantity'])))
            table.setItem(row, 4, QTableWidgetItem(str(item['unit_price'])))
        
        layout.addWidget(table)
        btn_close = QPushButton("关闭")
        btn_close.clicked.connect(self.close)
        layout.addWidget(btn_close)

# ==========================================
# 主页面：进货管理
# ==========================================
class PurchasePage(QWidget):
    def __init__(self):
        super().__init__()
        self.p_ctrl = PurchaseController()
        self.b_ctrl = BaseInfoController()
        self.draft_items = [] # 暂存当前拟入库的药品列表
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        
        # 两个主要页签
        self.tab_new = QWidget()
        self.tab_history = QWidget()
        
        self.init_new_order_ui()
        self.init_history_ui()
        
        self.tabs.addTab(self.tab_new, "录入新入库单")
        self.tabs.addTab(self.tab_history, "历史入库记录")
        
        layout.addWidget(self.tabs)
        
        # 初始加载
        self.refresh_combos()
        self.refresh_history()

    # ---------------------------
    # 选项卡1：录入新单逻辑
    # ---------------------------
    def init_new_order_ui(self):
        main_layout = QVBoxLayout(self.tab_new)
        
        # 1. 顶部表单（单据信息）
        top_group = QGroupBox("单据基本信息")
        form_layout = QFormLayout(top_group)
        
        self.input_order_id = QLineEdit()
        self.input_order_id.setPlaceholderText("例如：PO2024010101")
        
        self.combo_supplier = QComboBox()
        self.combo_employee = QComboBox()
        self.input_invoice = QLineEdit()
        self.input_remark = QLineEdit()
        
        form_layout.addRow("入库单号:", self.input_order_id)
        form_layout.addRow("选择供应商:", self.combo_supplier)
        form_layout.addRow("经办员工:", self.combo_employee)
        form_layout.addRow("发票号码:", self.input_invoice)
        form_layout.addRow("备注信息:", self.input_remark)
        
        # 2. 中部表单（添加药品）
        item_group = QGroupBox("添加药品明细")
        item_layout = QHBoxLayout(item_group)
        
        self.combo_medicine = QComboBox()
        self.input_qty = QSpinBox()
        self.input_qty.setRange(1, 99999)
        self.input_price = QDoubleSpinBox()
        self.input_price.setRange(0, 999999.99)
        self.btn_add_item = QPushButton("加入列表")
        self.btn_add_item.setStyleSheet("background-color: #2196F3; color: white;")
        self.btn_add_item.clicked.connect(self.add_item_to_draft)
        
        item_layout.addWidget(QLabel("药品:"))
        item_layout.addWidget(self.combo_medicine, 3)
        item_layout.addWidget(QLabel("数量:"))
        item_layout.addWidget(self.input_qty, 1)
        item_layout.addWidget(QLabel("采购单价:"))
        item_layout.addWidget(self.input_price, 1)
        item_layout.addWidget(self.btn_add_item, 1)

        # 3. 临时明细表格
        self.draft_table = QTableWidget()
        self.draft_table.setColumnCount(4)
        self.draft_table.setHorizontalHeaderLabels(["药品ID", "药品名称", "数量", "采购单价"])
        self.draft_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # 4. 底部提交按钮
        self.btn_submit = QPushButton("确认提交入库单")
        self.btn_submit.setFixedHeight(40)
        self.btn_submit.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.btn_submit.clicked.connect(self.submit_order)

        main_layout.addWidget(top_group)
        main_layout.addWidget(item_group)
        main_layout.addWidget(self.draft_table)
        main_layout.addWidget(self.btn_submit)

    def refresh_combos(self):
        """加载下拉框数据"""
        # 加载供应商
        s_ok, s_data = self.b_ctrl.fetch_all_suppliers()
        if s_ok:
            self.combo_supplier.clear()
            for s in s_data:
                self.combo_supplier.addItem(f"{s['supp_name']} ({s['supp_id']})", s['supp_id'])
            
        # 加载员工
        e_ok, e_data = self.b_ctrl.fetch_all_employees()
        if e_ok:
            self.combo_employee.clear()
            for e in e_data:
                self.combo_employee.addItem(f"{e['emp_name']} ({e['emp_id']})", e['emp_id'])
            
        # 加载药品
        m_ok, m_data = self.b_ctrl.fetch_all_medicines()
        if m_ok:
            self.combo_medicine.clear()
            for m in m_data:
                self.combo_medicine.addItem(f"{m['medicine_name']} ({m['medicine_id']})", m['medicine_id'])

    def add_item_to_draft(self):
        """将药品加入拟入库列表（前端展示）"""
        m_id = self.combo_medicine.currentData()
        m_name = self.combo_medicine.currentText().split(" (")[0]
        qty = self.input_qty.value()
        price = self.input_price.value()
        
        # 检查是否重复添加
        for item in self.draft_items:
            if item['medicine_id'] == m_id:
                QMessageBox.warning(self, "提示", "该药品已在列表中，请删除后再重新添加或修改数量")
                return

        item_data = {"medicine_id": m_id, "medicine_name": m_name, "quantity": qty, "unit_price": price}
        self.draft_items.append(item_data)
        
        # 更新表格
        row = self.draft_table.rowCount()
        self.draft_table.insertRow(row)
        self.draft_table.setItem(row, 0, QTableWidgetItem(m_id))
        self.draft_table.setItem(row, 1, QTableWidgetItem(m_name))
        self.draft_table.setItem(row, 2, QTableWidgetItem(str(qty)))
        self.draft_table.setItem(row, 3, QTableWidgetItem(str(price)))

    def submit_order(self):
        """提交整张入库单到数据库"""
        order_id = self.input_order_id.text().strip()
        supp_id = self.combo_supplier.currentData()
        emp_id = self.combo_employee.currentData()
        invoice = self.input_invoice.text().strip()
        remark = self.input_remark.text().strip()
        
        if not order_id or not self.draft_items:
            QMessageBox.warning(self, "错误", "单据号不能为空且必须包含至少一项药品明细")
            return

        # 确认提交
        success, msg = self.p_ctrl.submit_purchase(order_id, supp_id, emp_id, invoice, remark, self.draft_items)
        
        if success:
            QMessageBox.information(self, "成功", msg)
            # 清空界面
            self.input_order_id.clear()
            self.draft_table.setRowCount(0)
            self.draft_items = []
            self.refresh_history()
        else:
            QMessageBox.critical(self, "失败", msg)

    # ---------------------------
    # 选项卡2：历史查询逻辑
    # ---------------------------
    def init_history_ui(self):
        layout = QVBoxLayout(self.tab_history)
        
        tool_layout = QHBoxLayout()
        btn_refresh = QPushButton("刷新历史记录")
        btn_refresh.clicked.connect(self.refresh_history)
        tool_layout.addWidget(btn_refresh)
        tool_layout.addStretch()
        layout.addLayout(tool_layout)
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels(["单据号", "供应商", "操作员", "日期", "总金额", "发票号"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.history_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.history_table.doubleClicked.connect(self.show_order_detail)
        
        layout.addWidget(self.history_table)
        layout.addWidget(QLabel("提示：双击行可查看该订单的药品明细"))

    def refresh_history(self):
        # 核心修改：接收元组 (success, data)
        success, data = self.p_ctrl.get_purchase_history()
        
        if not success:
            # 如果失败，data 此时是错误字符串
            QMessageBox.critical(self, "查询失败", data)
            return

        # 成功时，data 才是真正的列表
        orders = data
        self.history_table.setRowCount(len(orders))
        for row, o in enumerate(orders):
            self.history_table.setItem(row, 0, QTableWidgetItem(str(o['order_id'])))
            self.history_table.setItem(row, 1, QTableWidgetItem(str(o['supp_name'])))
            self.history_table.setItem(row, 2, QTableWidgetItem(str(o['emp_name'])))
            self.history_table.setItem(row, 3, QTableWidgetItem(str(o['order_date'])))
            self.history_table.setItem(row, 4, QTableWidgetItem(str(o['total_amount'])))
            self.history_table.setItem(row, 5, QTableWidgetItem(str(o['invoice_number'])))

    def show_order_detail(self):
        row = self.history_table.currentRow()
        if row < 0: return
        order_id = self.history_table.item(row, 0).text()
        
        # 核心修改：解包元组
        success, items = self.p_ctrl.get_order_details(order_id)
        if success:
            dialog = PurchaseDetailDialog(order_id, items)
            dialog.exec()
        else:
            QMessageBox.warning(self, "错误", f"无法获取明细: {items}")