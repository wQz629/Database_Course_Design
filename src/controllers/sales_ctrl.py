# src/controllers/sales_ctrl.py
from src.database.dao import SalesDAO
from pymysql import MySQLError

class SalesController:
    def __init__(self):
        self.dao = SalesDAO()

    # --- 之前的提交和退货逻辑保持不变 ---
    def submit_sale(self, sales_id, cust_id, emp_id, remark, items):
        if not items: return False, "未选择任何药品！"
        try:
            self.dao.register_sale(sales_id, cust_id, emp_id, remark, items)
            return True, "销售结账成功！"
        except MySQLError as e:
            err_msg = e.args[1] if len(e.args) > 1 else str(e)
            return False, f"销售拦截：{err_msg}"

    def process_return(self, return_id, sales_id, emp_id, cust_id, amount, reason, items):
        try:
            self.dao.register_return(return_id, sales_id, emp_id, cust_id, amount, reason, items)
            return True, "退货处理完成。"
        except MySQLError as e:
            return False, str(e)

    # --- 查询相关函数 ---

    def get_history(self):
        """获取所有历史销售主单列表（用于主表格）"""
        try:
            return True, self.dao.get_sales_history()
        except Exception as e:
            return False, str(e)

    def get_order_details(self, sales_id):
        """
        【核心新增】查看具体某一笔销售单的药品明细
        用途：UI中点击某个订单时，下方或弹窗显示该单据买了哪些药
        """
        if not sales_id:
            return False, "销售单号不能为空"
        try:
            details = self.dao.get_sale_details(sales_id)
            if not details:
                return False, "未找到该订单的药品明细"
            return True, details
        except Exception as e:
            return False, f"查询明细失败: {str(e)}"