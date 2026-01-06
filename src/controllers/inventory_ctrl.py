# src/controllers/inventory_ctrl.py
from src.database.dao import InventoryDAO
from src.utils.logger import logger  # 导入日志模块
from pymysql import MySQLError

class InventoryController:
    def __init__(self):
        self.dao = InventoryDAO()

    def get_full_report(self):
        """获取全量库存列表"""
        logger.debug("正在请求全量库存报表数据...")
        try:
            data = self.dao.get_inventory_report()
            logger.info(f"全量库存报表加载成功 | 药品种类: {len(data)}")
            return True, data
        except Exception as e:
            logger.error(f"获取库存报表发生异常: {e}")
            return False, f"获取库存报表失败: {str(e)}"

    def fetch_stock_by_id(self, m_id):
        """获取指定药品的实时库存详情"""
        if not m_id:
            logger.warning("查询单个库存失败：未提供药品ID")
            return False, "药品ID不能为空"
            
        logger.debug(f"正在查询特定药品库存 | ID: {m_id}")
        try:
            res = self.dao.get_by_id(m_id)
            if not res:
                logger.info(f"查询结果为空 | 药品ID: {m_id} 尚未入库或不存在")
                return False, "该药品目前暂无库存记录（或尚未入库）"
            
            logger.info(f"查询库存成功 | ID: {m_id} | 当前数量: {res['stock_quantity']}")
            return True, res
        except MySQLError as e:
            logger.error(f"查询药品库存数据库报错 | ID: {m_id} | 错误: {e}")
            return False, f"查询数据库失败: {str(e)}"
        except Exception as e:
            logger.error(f"查询药品库存系统异常 | ID: {m_id} | 错误: {e}")
            return False, f"系统异常: {str(e)}"

    def check_low_stock(self, threshold=10):
        """
        逻辑处理：从全量数据中过滤出低于预警值的药品
        """
        logger.info(f"启动低库存自动扫描 | 预警阈值: {threshold}")
        try:
            all_data = self.dao.get_inventory_report()
            low_stock_list = [item for item in all_data if item['stock_quantity'] < threshold]
            
            if low_stock_list:
                logger.warning(f"库存预警！发现 {len(low_stock_list)} 种药品库存低于 {threshold}")
                for item in low_stock_list:
                    logger.debug(f"低库存详情 | 名称: {item['medicine_name']} | 剩余: {item['stock_quantity']}")
            else:
                logger.info("库存状态良好，未发现低库存药品")
                
            return True, low_stock_list
        except Exception as e:
            logger.error(f"执行低库存扫描时发生异常: {e}")
            return False, str(e)