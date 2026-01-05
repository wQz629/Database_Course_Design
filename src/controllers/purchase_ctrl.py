# src/controllers/purchase_ctrl.py
from src.database.dao import PurchaseDAO
from pymysql import MySQLError

class PurchaseController:
    def __init__(self):
        self.dao = PurchaseDAO()

    def submit_purchase(self, order_id, supp_id, emp_id, invoice, remark, items):
        if not items: return False, "进货明细不能为空！"
        try:
            self.dao.register_purchase(order_id, supp_id, emp_id, invoice, remark, items)
            return True, "入库登记成功！"
        except MySQLError as e:
            err_msg = e.args[1] if len(e.args) > 1 else str(e)
            return False, f"入库失败：{err_msg}"

    # --- 查询相关函数 ---

    def get_purchase_history(self):
        """获取所有进货主单列表"""
        try:
            return True, self.dao.get_all_orders()
        except Exception as e:
            return False, str(e)

    def get_order_details(self, order_id):
        """
        【核心新增】查看具体某一笔进货单的药品明细
        用途：在进货历史界面，点击某行显示这一单进了哪些药、单价是多少
        """
        if not order_id:
            return False, "进货单号不能为空"
        try:
            details = self.dao.get_order_details(order_id)
            if not details:
                return False, "未找到该进货单明细"
            return True, details
        except Exception as e:
            return False, f"查询明细失败: {str(e)}"