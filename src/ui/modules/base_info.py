# src/ui/modules/base_info.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTabWidget, QDialog, QFormLayout, 
                             QLineEdit, QDateEdit, QDoubleSpinBox, QComboBox, QPushButton)
from PyQt6.QtCore import QDate
from src.controllers.base_info_ctrl import BaseInfoController
from src.ui.widgets.base_data_tab import BaseDataTab

# ==========================================
# 辅助类：通用输入对话框
# ==========================================
class DataInputDialog(QDialog):
    def __init__(self, title, fields, initial_data=None, is_edit=False):
        super().__init__()
        self.setWindowTitle(title)
        self.setFixedWidth(400)
        self.layout = QFormLayout(self)
        self.inputs = {}

        for field_key, label_text, field_type in fields:
            if field_type == "text":
                widget = QLineEdit()
                if initial_data: widget.setText(str(initial_data.get(field_key, "")))
                if is_edit and "id" in field_key.lower(): widget.setEnabled(False)
            elif field_type == "date":
                widget = QDateEdit()
                widget.setCalendarPopup(True)
                widget.setDisplayFormat("yyyy-MM-dd")
                if initial_data:
                    date_val = initial_data.get(field_key)
                    widget.setDate(QDate.fromString(str(date_val), "yyyy-MM-dd"))
                else:
                    widget.setDate(QDate.currentDate())
            elif field_type == "number":
                widget = QDoubleSpinBox()
                widget.setRange(0, 999999.99)
                if initial_data: widget.setValue(float(initial_data.get(field_key, 0)))
            elif field_type == "gender":
                widget = QComboBox()
                widget.addItems(["M", "F"])
                if initial_data: widget.setCurrentText(initial_data.get(field_key, "M"))
            
            self.layout.addRow(label_text, widget)
            self.inputs[field_key] = widget

        self.btn_save = QPushButton("提交")
        self.btn_save.clicked.connect(self.accept)
        self.layout.addRow(self.btn_save)

    def get_data(self):
        result = {}
        for key, widget in self.inputs.items():
            if isinstance(widget, QLineEdit): result[key] = widget.text()
            elif isinstance(widget, QDateEdit): result[key] = widget.date().toString("yyyy-MM-dd")
            elif isinstance(widget, QDoubleSpinBox): result[key] = widget.value()
            elif isinstance(widget, QComboBox): result[key] = widget.currentText()
        return result

# ==========================================
# 主页面：基础信息管理
# ==========================================
class BaseInfoPage(QWidget):
    def __init__(self):
        super().__init__()
        self.ctrl = BaseInfoController()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()

        # 核心配置：定义四个模块的显示和接口
        configs = [
            {
                "name": "药品",
                "layout_type": "adaptive",
                "headers": ["药品ID", "通用名", "分类", "规格", "厂家", "生产日期", "有效期", "零售价", "备注"],
                "fields": [
                    ("medicine_id", "编号", "text"), ("medicine_name", "名称", "text"), 
                    ("category", "分类", "text"), ("specification", "规格", "text"), 
                    ("manufacturer", "厂家", "text"), ("production_date", "生产日期", "date"), 
                    ("expiry_date", "有效期", "date"), ("retail_price", "价格", "number"), 
                    ("description", "备注", "text")
                ],
                "methods": {
                    "fetch_all": self.ctrl.fetch_all_medicines,
                    "fetch_by_id": self.ctrl.fetch_medicine_by_id,
                    "add": self.ctrl.add_medicine,
                    "update": self.ctrl.update_medicine,
                    "delete": self.ctrl.delete_medicine
                }
            },
            {
                "name": "员工",
                "layout_type": "stretch",
                "headers": ["工号", "姓名", "性别", "电话", "职位"],
                "fields": [
                    ("emp_id", "工号", "text"), ("emp_name", "姓名", "text"), 
                    ("gender", "性别", "gender"), ("phone", "电话", "text"), 
                    ("position", "职位", "text")
                ],
                "methods": {
                    "fetch_all": self.ctrl.fetch_all_employees,
                    "fetch_by_id": self.ctrl.fetch_employee_by_id,
                    "add": self.ctrl.add_employee,
                    "update": self.ctrl.update_employee,
                    "delete": self.ctrl.delete_employee
                }
            },
            {
                "name": "客户",
                "layout_type": "adaptive", 
                "headers": ["客户ID", "姓名", "电话", "地址"],
                "fields": [
                    ("cust_id", "编号", "text"), ("cust_name", "名称", "text"), 
                    ("phone", "电话", "text"), ("address", "地址", "text")
                ],
                "methods": {
                    "fetch_all": self.ctrl.fetch_all_customers,
                    "fetch_by_id": self.ctrl.fetch_customer_by_id,
                    "add": self.ctrl.add_customer,
                    "update": self.ctrl.update_customer,
                    "delete": self.ctrl.delete_customer
                }
            },
            {
                "name": "供应商",
                "layout_type": "stretch",
                "headers": ["供应商ID", "单位名称", "联系人", "电话", "地址", "银行账号"],
                "fields": [
                    ("supp_id", "编号", "text"), ("supp_name", "名称", "text"), 
                    ("contact_person", "联系人", "text"), ("phone", "电话", "text"), 
                    ("address", "地址", "text"), ("account", "账号", "text")
                ],
                "methods": {
                    "fetch_all": self.ctrl.fetch_all_suppliers,
                    "fetch_by_id": self.ctrl.fetch_supplier_by_id,
                    "add": self.ctrl.add_supplier,
                    "update": self.ctrl.update_supplier,
                    "delete": self.ctrl.delete_supplier
                }
            }
        ]

        # 循环生成四个 Tab
        self.tab_widgets = []
        for cfg in configs:
            tab = BaseDataTab(cfg['name'], cfg['layout_type'], cfg['headers'], cfg['fields'], cfg['methods'])
            self.tabs.addTab(tab, f"{cfg['name']}管理")
            self.tab_widgets.append(tab)

        # 切换选项卡时自动刷新数据
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        # 初始刷新第一页
        self.tab_widgets[0].refresh_data()

        layout.addWidget(self.tabs)

    def on_tab_changed(self, index):
        self.tab_widgets[index].refresh_data()