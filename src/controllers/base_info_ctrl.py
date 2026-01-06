# src/controllers/base_info_ctrl.py
from src.database.dao import MedicineDAO, EmployeeDAO, CustomerDAO, SupplierDAO
from src.utils.logger import logger  # 导入日志模块
from pymysql import MySQLError

class BaseInfoController:
    def __init__(self):
        self.medicine_dao = MedicineDAO()
        self.employee_dao = EmployeeDAO()
        self.customer_dao = CustomerDAO()
        self.supplier_dao = SupplierDAO()

    # ==========================
    # 1. 药品管理 (Medicine)
    # ==========================
    def add_medicine(self, data):
        """data: tuple (id, name, cat, spec, manu, p_date, e_date, price, desc)"""
        if not data[0] or not data[1]:
            return False, "药品编号和名称不能为空！"
        try:
            self.medicine_dao.add(*data)
            # 记录成功日志 (INFO)
            logger.info(f"添加药品成功 | ID: {data[0]} | 名称: {data[1]}")
            return True, "药品添加成功"
        except MySQLError as e:
            err_msg = str(e.args[1] if len(e.args)>1 else e)
            # 记录业务拦截日志 (WARNING)
            logger.warning(f"添加药品被拦截 | ID: {data[0]} | 原因: {err_msg}")
            return False, f"数据库错误: {err_msg}"
        except Exception as e:
            # 记录系统崩溃日志 (ERROR)
            logger.error(f"添加药品发生系统异常 | ID: {data[0]} | 错误: {e}")
            return False, str(e)

    def update_medicine(self, m_id, data_dict):
        try:
            self.medicine_dao.update(m_id, data_dict)
            logger.info(f"修改药品成功 | ID: {m_id} | 修改项: {list(data_dict.keys())}")
            return True, "药品修改成功"
        except Exception as e:
            logger.error(f"修改药品异常 | ID: {m_id} | 错误: {e}")
            return False, f"修改失败: {str(e)}"

    def delete_medicine(self, m_id):
        try:
            self.medicine_dao.delete(m_id)
            # 删除属于敏感操作，建议记录为 WARNING
            logger.warning(f"数据删除 | 管理员删除了药品: {m_id}")
            return True, "删除成功"
        except MySQLError:
            logger.error(f"删除药品失败(外键约束) | ID: {m_id}")
            return False, "删除失败：该药品可能已有业务关联（如库存或销售记录）。"
        except Exception as e:
            logger.error(f"删除药品系统异常 | ID: {m_id} | 错误: {e}")
            return False, str(e)

    def fetch_all_medicines(self):
        try:
            data = self.medicine_dao.get_all()
            return True, data
        except Exception as e:
            logger.error(f"获取药品列表失败 | 错误: {e}")
            return False, str(e)

    def fetch_medicine_by_id(self, m_id):
        try:
            res = self.medicine_dao.get_by_id(m_id)
            if not res: 
                return False, "未找到该药品信息"
            return True, res
        except Exception as e:
            logger.error(f"查询单个药品失败 | ID: {m_id} | 错误: {e}")
            return False, f"查询失败: {str(e)}"

    # ==========================
    # 2. 员工管理 (Employee)
    # ==========================
    def add_employee(self, data):
        """data: tuple (emp_id, name, gender, phone, pos)"""
        if not data[0] or not data[1]:
            return False, "员工编号和姓名不能为空！"
        try:
            self.employee_dao.add(*data)
            logger.info(f"录入员工成功 | 工号: {data[0]} | 姓名: {data[1]}")
            return True, "员工录入成功"
        except Exception as e:
            logger.error(f"录入员工失败 | 工号: {data[0]} | 错误: {e}")
            return False, f"录入失败: {str(e)}"

    def update_employee(self, e_id, data_dict):
        try:
            self.employee_dao.update(e_id, data_dict)
            logger.info(f"修改员工信息成功 | 工号: {e_id}")
            return True, "员工信息修改成功"
        except Exception as e:
            logger.error(f"修改员工信息失败 | 工号: {e_id} | 错误: {e}")
            return False, f"修改失败: {str(e)}"

    def delete_employee(self, e_id):
        try:
            self.employee_dao.delete(e_id)
            logger.warning(f"数据删除 | 管理员删除了员工: {e_id}")
            return True, "员工删除成功"
        except Exception as e:
            logger.error(f"删除员工失败 | 工号: {e_id} | 错误: {e}")
            return False, "无法删除：该员工已有经办的单据记录。"

    def fetch_all_employees(self):
        try:
            data = self.employee_dao.get_all()
            return True, data
        except Exception as e:
            logger.error(f"获取员工列表失败 | 错误: {e}")
            return False, str(e)

    def fetch_employee_by_id(self, e_id):
        try:
            res = self.employee_dao.get_by_id(e_id)
            if not res: return False, "员工不存在"
            return True, res
        except Exception as e:
            logger.error(f"查询单个员工失败 | 工号: {e_id} | 错误: {e}")
            return False, str(e)

    # ==========================
    # 3. 客户管理 (Customer)
    # ==========================
    def add_customer(self, data):
        """data: tuple (cust_id, name, phone, address)"""
        if not data[0] or not data[1]:
            return False, "客户编号和名称不能为空！"
        try:
            self.customer_dao.add(*data)
            logger.info(f"创建客户档案成功 | ID: {data[0]} | 姓名: {data[1]}")
            return True, "客户档案创建成功"
        except Exception as e:
            logger.error(f"创建客户档案失败 | ID: {data[0]} | 错误: {e}")
            return False, f"创建失败: {str(e)}"

    def update_customer(self, c_id, data_dict):
        try:
            self.customer_dao.update(c_id, data_dict)
            logger.info(f"更新客户信息成功 | ID: {c_id}")
            return True, "客户信息更新成功"
        except Exception as e:
            logger.error(f"更新客户信息失败 | ID: {c_id} | 错误: {e}")
            return False, f"更新失败: {str(e)}"

    def delete_customer(self, c_id):
        try:
            self.customer_dao.delete(c_id)
            logger.warning(f"数据删除 | 管理员删除了客户: {c_id}")
            return True, "客户记录已删除"
        except Exception as e:
            logger.error(f"删除客户失败 | ID: {c_id} | 错误: {e}")
            return False, "无法删除：该客户已有消费记录。"

    def fetch_all_customers(self):
        try:
            data = self.customer_dao.get_all()
            return True, data
        except Exception as e:
            logger.error(f"获取客户列表失败 | 错误: {e}")
            return False, str(e)

    def fetch_customer_by_id(self, c_id):
        try:
            res = self.customer_dao.get_by_id(c_id)
            if not res: return False, "客户不存在"
            return True, res
        except Exception as e:
            logger.error(f"查询单个客户失败 | ID: {c_id} | 错误: {e}")
            return False, str(e)

    # ==========================
    # 4. 供应商管理 (Supplier)
    # ==========================
    def add_supplier(self, data):
        """data: tuple (supp_id, name, contact, phone, address, account)"""
        if not data[0] or not data[1]:
            return False, "供应商编号和名称不能为空！"
        try:
            self.supplier_dao.add(*data)
            logger.info(f"登记供应商成功 | ID: {data[0]} | 名称: {data[1]}")
            return True, "供应商登记成功"
        except Exception as e:
            logger.error(f"登记供应商失败 | ID: {data[0]} | 错误: {e}")
            return False, f"登记失败: {str(e)}"

    def update_supplier(self, s_id, data_dict):
        try:
            self.supplier_dao.update(s_id, data_dict)
            logger.info(f"修改供应商信息成功 | ID: {s_id}")
            return True, "供应商信息已修改"
        except Exception as e:
            logger.error(f"修改供应商信息失败 | ID: {s_id} | 错误: {e}")
            return False, f"修改失败: {str(e)}"

    def delete_supplier(self, s_id):
        try:
            self.supplier_dao.delete(s_id)
            logger.warning(f"数据删除 | 管理员删除了供应商: {s_id}")
            return True, "供应商已从名录中移除"
        except Exception as e:
            logger.error(f"删除供应商失败 | ID: {s_id} | 错误: {e}")
            return False, "无法删除：该供应商已有供货关联单据。"

    def fetch_all_suppliers(self):
        try:
            data = self.supplier_dao.get_all()
            return True, data
        except Exception as e:
            logger.error(f"获取供应商列表失败 | 错误: {e}")
            return False, str(e)

    def fetch_supplier_by_id(self, s_id):
        try:
            res = self.supplier_dao.get_by_id(s_id)
            if not res: return False, "供应商不存在"
            return True, res
        except Exception as e:
            logger.error(f"查询单个供应商失败 | ID: {s_id} | 错误: {e}")
            return False, str(e)