# src/database/dao.py
from .db_manager import DBManager

class BaseDAO:
    def __init__(self):
        self.db = DBManager()

# ==========================================
# 1. 基础信息管理模块 (Medicine, Employee, Customer, Supplier)
# ==========================================

class MedicineDAO(BaseDAO):
    def get_all(self):
        with self.db.session() as cursor:
            cursor.execute("SELECT * FROM medicine")
            return cursor.fetchall()

    def get_by_id(self, m_id):
        with self.db.session() as cursor:
            cursor.execute("SELECT * FROM medicine WHERE medicine_id = %s", (m_id,))
            return cursor.fetchone()

    def add(self, m_id, name, cat, spec, manu, p_date, e_date, price, desc):
        """现在接收 9 个明确的参数"""
        with self.db.session() as cursor:
            sql = "INSERT INTO medicine VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            # 将这些参数打包成元组交给 pymysql 执行
            cursor.execute(sql, (m_id, name, cat, spec, manu, p_date, e_date, price, desc))

    def update(self, m_id, data_dict):
        """data_dict: 包含要更新的字段及其值"""
        with self.db.session() as cursor:
            fields = ", ".join([f"{k} = %s" for k in data_dict.keys()])
            sql = f"UPDATE medicine SET {fields} WHERE medicine_id = %s"
            cursor.execute(sql, list(data_dict.values()) + [m_id])

    def delete(self, m_id):
        with self.db.session() as cursor:
            cursor.execute("DELETE FROM medicine WHERE medicine_id = %s", (m_id,))

class EmployeeDAO(BaseDAO):
    def get_all(self):
        with self.db.session() as cursor:
            cursor.execute("SELECT * FROM employee")
            return cursor.fetchall()

    def get_by_id(self, emp_id):
        with self.db.session() as cursor:
            cursor.execute("SELECT * FROM employee WHERE emp_id = %s", (emp_id,))
            return cursor.fetchone()
    
    def add(self, emp_id, name, gender, phone, pos):
        with self.db.session() as cursor:
            sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (emp_id, name, gender, phone, pos))

    def update(self, emp_id, data_dict):
        with self.db.session() as cursor:
            fields = ", ".join([f"{k} = %s" for k in data_dict.keys()])
            sql = f"UPDATE employee SET {fields} WHERE emp_id = %s"
            cursor.execute(sql, list(data_dict.values()) + [emp_id])

    def delete(self, emp_id):
        with self.db.session() as cursor:
            cursor.execute("DELETE FROM employee WHERE emp_id = %s", (emp_id,))

class CustomerDAO(BaseDAO):
    def get_all(self):
        with self.db.session() as cursor:
            cursor.execute("SELECT * FROM customer")
            return cursor.fetchall()

    def get_by_id(self, cust_id):
        with self.db.session() as cursor:
            cursor.execute("SELECT * FROM customer WHERE cust_id = %s", (cust_id,))
            return cursor.fetchone()
    
    def add(self, cust_id, name, phone, addr):
        with self.db.session() as cursor:
            sql = "INSERT INTO customer VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (cust_id, name, phone, addr))

    def update(self, cust_id, data_dict):
        with self.db.session() as cursor:
            fields = ", ".join([f"{k} = %s" for k in data_dict.keys()])
            sql = f"UPDATE customer SET {fields} WHERE cust_id = %s"
            cursor.execute(sql, list(data_dict.values()) + [cust_id])

    def delete(self, cust_id):
        with self.db.session() as cursor:
            cursor.execute("DELETE FROM customer WHERE cust_id = %s", (cust_id,))

class SupplierDAO(BaseDAO):
    def get_all(self):
        with self.db.session() as cursor:
            cursor.execute("SELECT * FROM supplier")
            return cursor.fetchall()

    def get_by_id(self, supp_id):
        with self.db.session() as cursor:
            cursor.execute("SELECT * FROM supplier WHERE supp_id = %s", (supp_id,))
            return cursor.fetchone()
    
    def add(self, supp_id, name, contact, phone, addr, acc):
        with self.db.session() as cursor:
            sql = "INSERT INTO supplier VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (supp_id, name, contact, phone, addr, acc))

    def update(self, supp_id, data_dict):
        with self.db.session() as cursor:
            fields = ", ".join([f"{k} = %s" for k in data_dict.keys()])
            sql = f"UPDATE supplier SET {fields} WHERE supp_id = %s"
            cursor.execute(sql, list(data_dict.values()) + [supp_id])

    def delete(self, supp_id):
        with self.db.session() as cursor:
            cursor.execute("DELETE FROM supplier WHERE supp_id = %s", (supp_id,))


# ==========================================
# 2. 进货管理模块 (Purchase)
# ==========================================

class PurchaseDAO(BaseDAO):
    def get_all_orders(self):
        """查询所有进货记录（主表）"""
        sql = """
            SELECT p.*, s.supp_name, e.emp_name 
            FROM purchase_order p
            JOIN supplier s ON p.supp_id = s.supp_id
            JOIN employee e ON p.emp_id = e.emp_id
            ORDER BY p.order_date DESC
        """
        with self.db.session() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()

    def get_order_details(self, order_id):
        """查询某一进货单的详细药品列表"""
        sql = """
            SELECT d.*, m.medicine_name, m.specification 
            FROM purchase_detail d
            JOIN medicine m ON d.medicine_id = m.medicine_id
            WHERE d.order_id = %s
        """
        with self.db.session() as cursor:
            cursor.execute(sql, (order_id,))
            return cursor.fetchall()

    def register_purchase(self, order_id, supp_id, emp_id, invoice, remark, items):
        """
        items: [{'medicine_id': 'M01', 'quantity': 10, 'unit_price': 5.0}, ...]
        触发器会自动处理: 供应商校验、总金额计算、库存增加
        """
        with self.db.session() as cursor:
            sql_main = """INSERT INTO purchase_order (order_id, supp_id, emp_id, total_amount, invoice_number, remark) 
                          VALUES (%s, %s, %s, 0, %s, %s)"""
            cursor.execute(sql_main, (order_id, supp_id, emp_id, invoice, remark))

            sql_detail = "INSERT INTO purchase_detail (order_id, medicine_id, quantity, unit_price) VALUES (%s, %s, %s, %s)"
            for item in items:
                cursor.execute(sql_detail, (order_id, item['medicine_id'], item['quantity'], item['unit_price']))


# ==========================================
# 3. 库存管理模块 (Inventory)
# ==========================================

# src/database/dao.py 

class InventoryDAO(BaseDAO):
    def get_inventory_report(self):
        """查看当前所有库存状态（全表）"""
        sql = """
            SELECT m.medicine_id, m.medicine_name, m.specification, m.manufacturer, 
                   i.stock_quantity, m.expiry_date
            FROM inventory i
            JOIN medicine m ON i.medicine_id = m.medicine_id
            ORDER BY i.stock_quantity ASC
        """
        with self.db.session() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()

    def get_by_id(self, m_id):
        """查看单个药品的库存详情"""
        sql = """
            SELECT m.medicine_id, m.medicine_name, m.specification, m.manufacturer, 
                   i.stock_quantity, m.expiry_date
            FROM inventory i
            JOIN medicine m ON i.medicine_id = m.medicine_id
            WHERE i.medicine_id = %s
        """
        with self.db.session() as cursor:
            cursor.execute(sql, (m_id,))
            return cursor.fetchone() # 返回单条记录字典


# ==========================================
# 4. 销售管理模块 (Sales & Return)
# ==========================================

class SalesDAO(BaseDAO):
    def get_sales_history(self):
        """查询销售历史主单"""
        sql = """
            SELECT s.*, c.cust_name, e.emp_name 
            FROM sales_order s
            JOIN customer c ON s.cust_id = c.cust_id
            JOIN employee e ON s.emp_id = e.emp_id
            ORDER BY s.sales_date DESC
        """
        with self.db.session() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()

    def get_sale_details(self, sales_id):
        """查询某一销售单的药品明细"""
        sql = """
            SELECT d.*, m.medicine_name 
            FROM sales_detail d
            JOIN medicine m ON d.medicine_id = m.medicine_id
            WHERE d.sales_id = %s
        """
        with self.db.session() as cursor:
            cursor.execute(sql, (sales_id,))
            return cursor.fetchall()
        
    def get_return_history(self):
        """查询所有退货记录"""
        sql = """
            SELECT r.*, c.cust_name, e.emp_name 
            FROM sales_return r
            JOIN customer c ON r.cust_id = c.cust_id
            JOIN employee e ON r.emp_id = e.emp_id
            ORDER BY r.return_date DESC
        """
        with self.db.session() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()

    def get_return_details(self, return_id):
        """查询某一退货单的药品明细"""
        sql = """
            SELECT rd.medicine_id, m.medicine_name, rd.return_quantity
            FROM sales_return_detail rd
            JOIN medicine m ON rd.medicine_id = m.medicine_id
            WHERE rd.return_id = %s
        """
        with self.db.session() as cursor:
            cursor.execute(sql, (return_id,))
            return cursor.fetchall()

    def register_sale(self, sales_id, cust_id, emp_id, remark, items):
        """
        触发器 tri_sales_reduce_stock 会自动拦截库存不足的插入
        """
        with self.db.session() as cursor:
            sql_main = "INSERT INTO sales_order (sales_id, cust_id, emp_id, total_amount, remark) VALUES (%s, %s, %s, 0, %s)"
            cursor.execute(sql_main, (sales_id, cust_id, emp_id, remark))

            sql_detail = "INSERT INTO sales_detail (sales_id, medicine_id, quantity, unit_price) VALUES (%s, %s, %s, %s)"
            for item in items:
                cursor.execute(sql_detail, (sales_id, item['medicine_id'], item['quantity'], item['unit_price']))

    def register_return(self, return_id, sales_id, emp_id, cust_id, total_amount, reason, items):
        with self.db.session() as cursor:
            sql_main = "INSERT INTO sales_return (return_id, sales_id, emp_id, cust_id, total_amount, reason) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(sql_main, (return_id, sales_id, emp_id, cust_id, total_amount, reason))

            sql_detail = "INSERT INTO sales_return_detail (return_id, medicine_id, return_quantity) VALUES (%s, %s, %s)"
            for item in items:
                cursor.execute(sql_detail, (return_id, item['medicine_id'], item['return_quantity']))


# ==========================================
# 5. 财务统计模块 (Finance)
# ==========================================

class FinanceDAO(BaseDAO):
    def get_daily_summaries(self):
        with self.db.session() as cursor:
            cursor.execute("SELECT * FROM sales_daily_summary ORDER BY summary_date DESC")
            return cursor.fetchall()

    def get_monthly_report(self, year, month):
        with self.db.session() as cursor:
            sql = """
                SELECT 
                    SUM(total_sales_amount) as month_sales,
                    SUM(total_return_amount) as month_return,
                    SUM(net_amount) as month_net,
                    SUM(order_count) as month_orders
                FROM sales_daily_summary 
                WHERE YEAR(summary_date) = %s AND MONTH(summary_date) = %s
            """
            cursor.execute(sql, (year, month))
            return cursor.fetchone()