from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QLineEdit, QLabel, 
                             QHeaderView, QTabWidget, QMessageBox, QComboBox, 
                             QDoubleSpinBox, QSpinBox, QGroupBox, QFormLayout, QDialog)
from PyQt6.QtCore import Qt
from src.controllers.sales_ctrl import SalesController
from src.controllers.base_info_ctrl import BaseInfoController
from src.controllers.inventory_ctrl import InventoryController

# ==========================================
# 辅助类：销售明细查看弹窗 (查销售了哪些药)
# ==========================================
class SalesDetailDialog(QDialog):
    def __init__(self, sales_id, items):
        super().__init__()
        self.setWindowTitle(f"销售单明细 - {sales_id}")
        self.resize(600, 400)
        layout = QVBoxLayout(self)
        
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["药品ID", "药品名称", "数量", "成交单价"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        table.setRowCount(len(items))
        for row, item in enumerate(items):
            table.setItem(row, 0, QTableWidgetItem(str(item['medicine_id'])))
            table.setItem(row, 1, QTableWidgetItem(str(item['medicine_name'])))
            table.setItem(row, 2, QTableWidgetItem(str(item['quantity'])))
            table.setItem(row, 3, QTableWidgetItem(f"￥{float(item['unit_price']):.2f}"))
        
        layout.addWidget(table)
        btn_close = QPushButton("关闭")
        btn_close.clicked.connect(self.close)
        layout.addWidget(btn_close)

# ==========================================
# 辅助类：退货明细查看弹窗 (查退回了哪些药)
# ==========================================
class ReturnDetailDialog(QDialog):
    def __init__(self, return_id, items):
        super().__init__()
        self.setWindowTitle(f"退货单明细 - {return_id}")
        self.resize(500, 350)
        layout = QVBoxLayout(self)
        
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["药品ID", "药品名称", "退回数量"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        table.setRowCount(len(items))
        for row, item in enumerate(items):
            table.setItem(row, 0, QTableWidgetItem(str(item['medicine_id'])))
            table.setItem(row, 1, QTableWidgetItem(str(item['medicine_name'])))
            table.setItem(row, 2, QTableWidgetItem(str(item['return_quantity'])))
        
        layout.addWidget(table)
        btn_close = QPushButton("关闭")
        btn_close.clicked.connect(self.close)
        layout.addWidget(btn_close)

# ==========================================
# 辅助类：办理退货对话框 (操作界面)
# ==========================================
class ReturnDialog(QDialog):
    def __init__(self, sale_info, items):
        super().__init__()
        self.setWindowTitle(f"办理退货 - 原单据：{sale_info['sales_id']}")
        self.resize(750, 500)
        self.sale_info = sale_info 
        self.items = items         
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        info_group = QGroupBox("退货单据信息")
        form = QFormLayout(info_group)
        self.input_return_id = QLineEdit()
        self.input_return_id.setPlaceholderText("退货单号(如 RE20260001)")
        self.input_reason = QLineEdit()
        self.input_reason.setPlaceholderText("退货原因说明")
        
        form.addRow("退货单号:", self.input_return_id)
        form.addRow("退货原因:", self.input_reason)
        layout.addWidget(info_group)

        item_group = QGroupBox("选择退货数量")
        item_layout = QVBoxLayout(item_group)
        self.item_table = QTableWidget()
        self.item_table.setColumnCount(5)
        self.item_table.setHorizontalHeaderLabels(["药品ID", "名称", "原购买量", "单价", "本次退货数量"])
        self.item_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        self.item_table.setRowCount(len(self.items))
        for row, it in enumerate(self.items):
            self.item_table.setItem(row, 0, QTableWidgetItem(str(it['medicine_id'])))
            self.item_table.setItem(row, 1, QTableWidgetItem(str(it['medicine_name'])))
            self.item_table.setItem(row, 2, QTableWidgetItem(str(it['quantity'])))
            self.item_table.setItem(row, 3, QTableWidgetItem(str(it['unit_price'])))
            
            qty_input = QSpinBox()
            qty_input.setRange(0, int(it['quantity'])) 
            self.item_table.setCellWidget(row, 4, qty_input)
            
        item_layout.addWidget(self.item_table)
        layout.addWidget(item_group)

        btn_layout = QHBoxLayout()
        self.btn_submit = QPushButton("确认退货提交")
        self.btn_submit.setStyleSheet("background-color: #f44336; color: white; font-weight: bold; height: 35px;")
        self.btn_submit.clicked.connect(self.accept)
        btn_cancel = QPushButton("取消")
        btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addStretch(); btn_layout.addWidget(btn_cancel); btn_layout.addWidget(self.btn_submit)
        layout.addLayout(btn_layout)

    def get_return_data(self):
        total_refund = 0
        items_to_return = []
        for row in range(self.item_table.rowCount()):
            qty = self.item_table.cellWidget(row, 4).value()
            if qty > 0:
                m_id = self.item_table.item(row, 0).text()
                price = float(self.item_table.item(row, 3).text())
                total_refund += qty * price
                items_to_return.append({"medicine_id": m_id, "return_quantity": qty})
        
        return {
            "return_id": self.input_return_id.text().strip(),
            "sales_id": self.sale_info['sales_id'],
            "emp_id": self.sale_info['emp_id'],
            "cust_id": self.sale_info['cust_id'],
            "total_amount": total_refund,
            "reason": self.input_reason.text().strip(),
            "items": items_to_return
        }

# ==========================================
# 主页面：销售管理
# ==========================================
class SalesPage(QWidget):
    def __init__(self):
        super().__init__()
        self.s_ctrl = SalesController()
        self.b_ctrl = BaseInfoController()
        self.i_ctrl = InventoryController()
        self.cart_items = [] 
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        
        self.tab_new = QWidget()
        self.tab_history = QWidget()
        self.tab_returns = QWidget()
        
        self.init_new_sale_ui()
        self.init_history_ui()
        self.init_return_history_ui()
        
        self.tabs.addTab(self.tab_new, "前台收银/结账")
        self.tabs.addTab(self.tab_history, "销售流水记录")
        self.tabs.addTab(self.tab_returns, "退货历史查询")
        
        layout.addWidget(self.tabs)
        self.refresh_combos()
        self.refresh_history()
        self.refresh_return_history()

    # --- 选项卡1：收银逻辑 ---
    def init_new_sale_ui(self):
        main_layout = QVBoxLayout(self.tab_new)
        top_group = QGroupBox("单据基本信息")
        top_layout = QHBoxLayout(top_group)
        self.input_sales_id = QLineEdit()
        self.input_sales_id.setPlaceholderText("销售单号(10位)")
        self.combo_customer = QComboBox()
        self.combo_employee = QComboBox()
        top_layout.addWidget(QLabel("单号:")); top_layout.addWidget(self.input_sales_id)
        top_layout.addWidget(QLabel("客户:")); top_layout.addWidget(self.combo_customer)
        top_layout.addWidget(QLabel("经办人:")); top_layout.addWidget(self.combo_employee)

        item_group = QGroupBox("药品选购")
        item_layout = QHBoxLayout(item_group)
        self.combo_medicine = QComboBox()
        self.combo_medicine.setEditable(True)
        self.combo_medicine.currentIndexChanged.connect(self.on_medicine_selected)
        self.combo_medicine.setMinimumWidth(250)
        self.label_stock_info = QLabel("库存: -")
        self.input_qty = QSpinBox(); self.input_qty.setRange(1, 9999)
        self.input_price = QDoubleSpinBox(); self.input_price.setRange(0, 9999.99)
        self.btn_add_cart = QPushButton("加入清单"); self.btn_add_cart.clicked.connect(self.add_to_cart)

        item_layout.addWidget(QLabel("选择药品:")); item_layout.addWidget(self.combo_medicine)
        item_layout.addWidget(self.label_stock_info)
        item_layout.addWidget(QLabel("数量:")); item_layout.addWidget(self.input_qty)
        item_layout.addWidget(QLabel("单价:")); item_layout.addWidget(self.input_price)
        item_layout.addWidget(self.btn_add_cart)

        self.cart_table = QTableWidget(); self.cart_table.setColumnCount(5)
        self.cart_table.setHorizontalHeaderLabels(["ID", "名称", "数量", "单价", "小计"])
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        bottom_layout = QHBoxLayout()
        self.label_total = QLabel("总金额: 0.00 元")
        self.label_total.setStyleSheet("font-size: 18px; color: red; font-weight: bold;")
        self.btn_submit_sale = QPushButton("确认结账提交")
        self.btn_submit_sale.setFixedHeight(40); self.btn_submit_sale.setStyleSheet("background-color: #E91E63; color: white; font-weight: bold;")
        self.btn_submit_sale.clicked.connect(self.submit_sale)
        bottom_layout.addWidget(self.label_total); bottom_layout.addStretch(); bottom_layout.addWidget(self.btn_submit_sale)

        main_layout.addWidget(top_group); main_layout.addWidget(item_group); main_layout.addWidget(self.cart_table); main_layout.addLayout(bottom_layout)

    def on_medicine_selected(self):
        m_id = self.combo_medicine.currentData()
        if not m_id: return
        ok_i, i_info = self.i_ctrl.fetch_stock_by_id(m_id)
        ok_m, m_info = self.b_ctrl.fetch_medicine_by_id(m_id)
        if ok_i and ok_m:
            self.label_stock_info.setText(f"库存: {i_info['stock_quantity']}")
            self.input_price.setValue(float(m_info['retail_price']))
            self.input_qty.setMaximum(i_info['stock_quantity'])

    def add_to_cart(self):
        m_id = self.combo_medicine.currentData()
        if not m_id: return
        m_name = self.combo_medicine.currentText().split(" [")[0]
        qty, price = self.input_qty.value(), self.input_price.value()
        for item in self.cart_items:
            if item['medicine_id'] == m_id: return QMessageBox.warning(self, "提示", "药品已在清单中")
        self.cart_items.append({"medicine_id": m_id, "medicine_name": m_name, "quantity": qty, "unit_price": price})
        self.update_cart_table()

    def update_cart_table(self):
        self.cart_table.setRowCount(0); total = 0
        for row, item in enumerate(self.cart_items):
            sub = item['quantity'] * item['unit_price']; total += sub
            self.cart_table.insertRow(row)
            self.cart_table.setItem(row, 0, QTableWidgetItem(item['medicine_id']))
            self.cart_table.setItem(row, 1, QTableWidgetItem(item['medicine_name']))
            self.cart_table.setItem(row, 2, QTableWidgetItem(str(item['quantity'])))
            self.cart_table.setItem(row, 3, QTableWidgetItem(f"{item['unit_price']:.2f}"))
            self.cart_table.setItem(row, 4, QTableWidgetItem(f"{sub:.2f}"))
        self.label_total.setText(f"总金额: {total:.2f} 元")

    def submit_sale(self):
        sid, cid, eid = self.input_sales_id.text().strip(), self.combo_customer.currentData(), self.combo_employee.currentData()
        if not sid or not self.cart_items: return QMessageBox.warning(self, "错误", "请填写单号并添加药品")
        success, msg = self.s_ctrl.submit_sale(sid, cid, eid, "柜台零售", self.cart_items)
        if success:
            QMessageBox.information(self, "成功", "结账完成！")
            self.cart_items = []; self.input_sales_id.clear()
            self.update_cart_table(); self.refresh_history(); self.refresh_combos()
        else: QMessageBox.critical(self, "失败", msg)

    # --- 选项卡2：销售历史 ---
    def init_history_ui(self):
        layout = QVBoxLayout(self.tab_history)
        btn_layout = QHBoxLayout()
        btn_refresh = QPushButton("刷新流水"); btn_refresh.clicked.connect(self.refresh_history)
        btn_return = QPushButton("办理退货"); btn_return.setStyleSheet("background-color: #607D8B; color: white;")
        btn_return.clicked.connect(self.on_return_click)
        btn_layout.addWidget(btn_refresh); btn_layout.addWidget(btn_return); btn_layout.addStretch()
        self.history_table = QTableWidget(); self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(["单号", "客户", "收银员", "时间", "总额"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.history_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.history_table.doubleClicked.connect(self.show_sale_detail)
        layout.addLayout(btn_layout); layout.addWidget(self.history_table)

    def refresh_history(self):
        success, data = self.s_ctrl.get_history()
        if success:
            self.history_table.setRowCount(len(data))
            for row, d in enumerate(data):
                item_id = QTableWidgetItem(str(d['sales_id']))
                item_id.setData(Qt.ItemDataRole.UserRole, d) 
                self.history_table.setItem(row, 0, item_id)
                self.history_table.setItem(row, 1, QTableWidgetItem(str(d['cust_name'])))
                self.history_table.setItem(row, 2, QTableWidgetItem(str(d['emp_name'])))
                self.history_table.setItem(row, 3, QTableWidgetItem(str(d['sales_date'])))
                self.history_table.setItem(row, 4, QTableWidgetItem(f"￥{float(d['total_amount']):.2f}"))

    def show_sale_detail(self):
        row = self.history_table.currentRow()
        if row < 0: return
        sid = self.history_table.item(row, 0).text()
        success, items = self.s_ctrl.get_order_details(sid)
        if success: SalesDetailDialog(sid, items).exec()

    def on_return_click(self):
        row = self.history_table.currentRow()
        if row < 0: return QMessageBox.warning(self, "提示", "请选择销售单")
        sale_info = self.history_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        success, items = self.s_ctrl.get_order_details(sale_info['sales_id'])
        if success:
            dialog = ReturnDialog(sale_info, items)
            if dialog.exec():
                data = dialog.get_return_data()
                if not data['return_id'] or not data['items']: return
                res_ok, res_msg = self.s_ctrl.process_return(data['return_id'], data['sales_id'], data['emp_id'], data['cust_id'], data['total_amount'], data['reason'], data['items'])
                if res_ok:
                    QMessageBox.information(self, "成功", "退货已办理")
                    self.refresh_return_history(); self.refresh_history(); self.refresh_combos()
                else: QMessageBox.critical(self, "失败", res_msg)

    # --- 选项卡3：退货历史 (补全双击功能) ---
    def init_return_history_ui(self):
        layout = QVBoxLayout(self.tab_returns)
        tool = QHBoxLayout()
        btn = QPushButton("刷新退货历史"); btn.clicked.connect(self.refresh_return_history)
        tool.addWidget(btn); tool.addStretch()
        self.return_table = QTableWidget(); self.return_table.setColumnCount(6)
        self.return_table.setHorizontalHeaderLabels(["退货单号", "原销售单", "客户", "办理人", "退款额", "日期"])
        self.return_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.return_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        # 核心补全：绑定双击查看详情事件
        self.return_table.doubleClicked.connect(self.show_return_detail)
        layout.addLayout(tool); layout.addWidget(self.return_table)

    def refresh_return_history(self):
        success, data = self.s_ctrl.get_return_history()
        if success:
            self.return_table.setRowCount(len(data))
            for row, d in enumerate(data):
                self.return_table.setItem(row, 0, QTableWidgetItem(str(d['return_id'])))
                self.return_table.setItem(row, 1, QTableWidgetItem(str(d['sales_id'])))
                self.return_table.setItem(row, 2, QTableWidgetItem(str(d['cust_name'])))
                self.return_table.setItem(row, 3, QTableWidgetItem(str(d['emp_name'])))
                self.return_table.setItem(row, 4, QTableWidgetItem(f"￥{float(d['total_amount']):.2f}"))
                self.return_table.setItem(row, 5, QTableWidgetItem(str(d['return_date'])))

    def show_return_detail(self):
        """双击查看退货明细"""
        row = self.return_table.currentRow()
        if row < 0: return
        rid = self.return_table.item(row, 0).text()
        # 注意：这里需要 SalesController 有 get_return_details 方法
        success, items = self.s_ctrl.get_return_details(rid)
        if success:
            ReturnDetailDialog(rid, items).exec()
        else:
            QMessageBox.critical(self, "错误", f"查询失败: {items}")

    def refresh_combos(self):
        ok_c, c_list = self.b_ctrl.fetch_all_customers()
        if ok_c:
            self.combo_customer.clear()
            for c in c_list: self.combo_customer.addItem(c['cust_name'], c['cust_id'])
        ok_e, e_list = self.b_ctrl.fetch_all_employees()
        if ok_e:
            self.combo_employee.clear()
            for e in e_list: self.combo_employee.addItem(e['emp_name'], e['emp_id'])
        ok_i, i_list = self.i_ctrl.get_full_report()
        if ok_i:
            self.combo_medicine.clear()
            for item in i_list:
                if item['stock_quantity'] > 0:
                    self.combo_medicine.addItem(f"{item['medicine_name']} [{item['specification']}]", item['medicine_id'])
            self.on_medicine_selected()