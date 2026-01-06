# src/ui/widgets/base_data_tab.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QMessageBox, QHeaderView)
from PyQt6.QtCore import Qt


class BaseDataTab(QWidget):
    """
    通用数据管理组件：负责表格展示和增删改查的调度
    """
    def __init__(self, name, layout_type, headers, field_config, ctrl_methods):
        super().__init__()
        self.name = name
        self.headers = headers
        self.fields = field_config  # 字段配置，用于生成对话框
        self.ctrl = ctrl_methods    # 包含：fetch_all, fetch_by_id, add, update, delete
        self.layout_type = layout_type  # 保存布局类型
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 1. 顶部工具栏
        tool_layout = QHBoxLayout()
        self.btn_refresh = QPushButton("刷新列表")
        self.btn_add = QPushButton(f"新增{self.name}")
        self.btn_edit = QPushButton("修改选中")
        self.btn_delete = QPushButton("删除选中")
        
        for btn in [self.btn_refresh, self.btn_add, self.btn_edit, self.btn_delete]:
            tool_layout.addWidget(btn)
        tool_layout.addStretch()
        
        # 2. 表格
        self.table = QTableWidget()
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        
        # --- 根据布局类型设置表格头部 ---
        header = self.table.horizontalHeader()
        
        if self.layout_type == "adaptive":
            # 针对 药品、客户：自适应内容 + 最后一列拉伸
            header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
            header.setStretchLastSection(True)
        else:
            # 针对 员工、供应商：全表平分宽度 + 隐藏滚动条
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # ---------------------------------------

        # 允许最后一列拉伸填充剩余所有空白 (保证整体美观，无右侧黑洞)
        header.setStretchLastSection(True)
        
        layout.addLayout(tool_layout)
        layout.addWidget(self.table)

        # 绑定事件
        self.btn_refresh.clicked.connect(self.refresh_data)
        self.btn_add.clicked.connect(self.on_add)
        self.btn_edit.clicked.connect(self.on_edit)
        self.btn_delete.clicked.connect(self.on_delete)

    def refresh_data(self):
        """
        核心修改：处理 Controller 返回的 (success, data) 元组
        """
        # 1. 解包元组
        success, result = self.ctrl['fetch_all']()
        
        # 2. 判断是否成功
        if not success:
            QMessageBox.critical(self, "错误", f"无法加载{self.name}数据: {result}")
            return

        # 3. 这里的 result 才是真正的列表数据
        data_list = result
        
        self.table.setRowCount(0)
        self.table.setColumnCount(len(self.headers))
        self.table.setHorizontalHeaderLabels(self.headers)
        
        if not data_list: 
            return # 如果没数据，直接返回
        
        # 4. 遍历真正的列表数据
        for row_idx, row_dict in enumerate(data_list):
            self.table.insertRow(row_idx)
            # row_dict 现在确定是一个字典了
            for col_idx, value in enumerate(row_dict.values()):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value if value is not None else "")))

    def on_add(self):
        from ..modules.base_info import DataInputDialog
        dialog = DataInputDialog(f"新增{self.name}", self.fields)
        if dialog.exec():
            res = dialog.get_data()
            # 这里的 res 是一个字典，如 {'medicine_id': 'M01', 'name': 'xxx', ...}
            # 我们需要按照字段顺序提取值组成元组
            data_tuple = tuple(res.values())
            
            # 调用控制器
            success, msg = self.ctrl['add'](data_tuple)
            
            if success:
                QMessageBox.information(self, "操作结果", msg)
                self.refresh_data()
            else:
                QMessageBox.warning(self, "操作失败", msg)

    def on_edit(self):
        from ..modules.base_info import DataInputDialog
        row = self.table.currentRow()
        if row < 0: return QMessageBox.warning(self, "提示", "请选择要修改的行")
        pk_id = self.table.item(row, 0).text()
        
        success, info = self.ctrl['fetch_by_id'](pk_id)
        if success:
            dialog = DataInputDialog(f"修改{self.name}", self.fields, initial_data=info, is_edit=True)
            if dialog.exec():
                new_data = dialog.get_data()
                # 移除主键（通常是第一个字段）不参与更新
                pk_field_name = self.fields[0][0]
                new_data.pop(pk_field_name, None)
                success_upd, msg = self.ctrl['update'](pk_id, new_data)
                QMessageBox.information(self, "操作结果", msg)
                self.refresh_data()

    def on_delete(self):
        row = self.table.currentRow()
        if row < 0: return QMessageBox.warning(self, "提示", "请选择要删除的行")
        pk_id = self.table.item(row, 0).text()
        if QMessageBox.question(self, "确认", f"确定删除该{self.name}记录吗？") == QMessageBox.StandardButton.Yes:
            success, msg = self.ctrl['delete'](pk_id)
            QMessageBox.information(self, "结果", msg)
            self.refresh_data()