# src/controllers/inventory_ctrl.py
from src.database.dao import InventoryDAO
from pymysql import MySQLError

class InventoryController:
    def __init__(self):
        self.dao = InventoryDAO()

    def get_full_report(self):
        """获取全量库存列表"""
        try:
            data = self.dao.get_inventory_report()
            return True, data
        except Exception as e:
            return False, f"获取库存报表失败: {str(e)}"

    def fetch_stock_by_id(self, m_id):
        """【新增】获取指定药品的实时库存详情"""
        if not m_id:
            return False, "药品ID不能为空"
            
        try:
            res = self.dao.get_by_id(m_id)
            if not res:
                return False, "该药品目前暂无库存记录（或尚未入库）"
            return True, res
        except MySQLError as e:
            return False, f"查询数据库失败: {str(e)}"
        except Exception as e:
            return False, f"系统异常: {str(e)}"

    def check_low_stock(self, threshold=10):
        """
        逻辑处理：从全量数据中过滤出低于预警值的药品
        通常用于主界面右上角的报警提示
        """
        try:
            all_data = self.dao.get_inventory_report()
            low_stock_list = [item for item in all_data if item['stock_quantity'] < threshold]
            return True, low_stock_list
        except Exception as e:
            return False, str(e)