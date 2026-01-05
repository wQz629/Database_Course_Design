# src/controllers/base_info_ctrl.py
from src.database.dao import MedicineDAO, EmployeeDAO, CustomerDAO, SupplierDAO
from pymysql import MySQLError

class BaseInfoController:
    def __init__(self):
        self.medicine_dao = MedicineDAO()
        self.employee_dao = EmployeeDAO()
        self.customer_dao = CustomerDAO()
        self.supplier_dao = SupplierDAO()

    # ==========================
    # 药品管理 (Medicine)
    # ==========================
    def add_medicine(self, data):
        if not data[0] or not data[1]:
            return False, "药品编号和名称不能为空！"
        try:
            self.medicine_dao.add(data)
            return True, "添加成功"
        except MySQLError as e:
            return False, f"数据库错误: {str(e.args[1] if len(e.args)>1 else e)}"

    def update_medicine(self, m_id, data_dict):
        try:
            self.medicine_dao.update(m_id, data_dict)
            return True, "修改成功"
        except MySQLError as e:
            return False, f"修改失败: {str(e)}"

    def delete_medicine(self, m_id):
        try:
            self.medicine_dao.delete(m_id)
            return True, "删除成功"
        except MySQLError as e:
            return False, "删除失败：该药品可能已有业务关联（如库存或销售），无法删除。"

    def fetch_all_medicines(self):
        return self.medicine_dao.get_all()

    def fetch_medicine_by_id(self, m_id):
        """根据ID查询单个药品详情"""
        try:
            res = self.medicine_dao.get_by_id(m_id)
            if not res:
                return False, "未找到该药品信息"
            return True, res
        except MySQLError as e:
            return False, f"查询失败: {str(e)}"

    # ==========================
    # 员工管理 (Employee)
    # ==========================
    def add_employee(self, data):
        try:
            # data: (emp_id, name, gender, phone, pos)
            self.employee_dao.add(*data)
            return True, "员工录入成功"
        except MySQLError as e:
            return False, f"录入失败: {str(e)}"

    def fetch_employee_by_id(self, e_id):
        """单个员工查询"""
        try:
            res = self.employee_dao.get_by_id(e_id)
            if not res: return False, "员工不存在"
            return True, res
        except MySQLError as e:
            return False, str(e)

    # ... 同样的逻辑实现 update_employee, delete_employee, fetch_all_employees ...

    # ==========================
    # 客户管理 (Customer)
    # ==========================
    def add_customer(self, data):
        try:
            self.customer_dao.add(*data)
            return True, "客户档案创建成功"
        except MySQLError as e:
            return False, str(e)

    def fetch_customer_by_id(self, c_id):
        """单个客户查询"""
        try:
            res = self.customer_dao.get_by_id(c_id)
            if not res: return False, "客户不存在"
            return True, res
        except MySQLError as e:
            return False, str(e)

    # ... 实现 update_customer, delete_customer, fetch_all_customers ...

    # ==========================
    # 供应商管理 (Supplier)
    # ==========================
    def add_supplier(self, data):
        try:
            self.supplier_dao.add(*data)
            return True, "供应商登记成功"
        except MySQLError as e:
            return False, str(e)

    def fetch_supplier_by_id(self, s_id):
        """单个供应商查询"""
        try:
            res = self.supplier_dao.get_by_id(s_id)
            if not res: return False, "供应商不存在"
            return True, res
        except MySQLError as e:
            return False, str(e)