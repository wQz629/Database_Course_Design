# src/controllers/purchase_ctrl.py
from src.database.dao import PurchaseDAO
from src.utils.logger import logger 
from pymysql import MySQLError

class PurchaseController:
    def __init__(self):
        self.dao = PurchaseDAO()

    def submit_purchase(self, order_id, supp_id, emp_id, invoice, remark, items):
        """
        提交入库单并记录日志
        """
        if not items:
            logger.warning(f"入库尝试被拒绝：单号 {order_id} 没有任何药品明细")
            return False, "进货明细不能为空！"

        logger.info(f"开始执行入库登记 | 单号: {order_id} | 供应商ID: {supp_id} | 经办人ID: {emp_id}")
        
        try:
            # 执行 DAO 操作，这会触发数据库的库存增加和总价计算触发器
            self.dao.register_purchase(order_id, supp_id, emp_id, invoice, remark, items)
            
            logger.info(f"入库登记成功 | 单号: {order_id} | 品种数: {len(items)}")
            return True, "入库登记成功！"
            
        except MySQLError as e:
            # 捕获触发器抛出的异常（如：供应商不存在）
            err_msg = e.args[1] if len(e.args) > 1 else str(e)
            logger.warning(f"入库被拦截(触发器限制) | 单号: {order_id} | 原因: {err_msg}")
            return False, f"入库失败：{err_msg}"
            
        except Exception as e:
            # 捕获系统级异常（如：数据库断开）
            logger.error(f"入库程序执行崩溃 | 单号: {order_id} | 错误堆栈: {e}")
            return False, f"系统异常：{str(e)}"

    # --- 查询相关函数 ---
    def get_purchase_history(self):
        """获取所有进货主单列表"""
        logger.debug("正在请求进货历史列表...")
        try:
            data = self.dao.get_all_orders()
            logger.info(f"成功加载进货历史 | 记录数: {len(data)}")
            return True, data
        except Exception as e:
            logger.error(f"加载进货历史失败 | 错误: {e}")
            return False, str(e)

    def get_order_details(self, order_id):
        """查看具体某一笔进货单的药品明细"""
        if not order_id:
            return False, "进货单号不能为空"

        logger.debug(f"正在查询进货明细详情 | 单号: {order_id}")
        try:
            details = self.dao.get_order_details(order_id)
            if not details:
                logger.warning(f"明细查询结果为空 | 单号: {order_id}")
                return False, "未找到该进货单明细"
                
            logger.info(f"明细查询成功 | 单号: {order_id} | 项目数: {len(details)}")
            return True, details
        except Exception as e:
            logger.error(f"查询单据 {order_id} 明细时发生系统错误: {e}")
            return False, f"查询明细失败: {str(e)}"