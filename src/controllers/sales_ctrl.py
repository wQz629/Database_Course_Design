# src/controllers/sales_ctrl.py
from src.database.dao import SalesDAO
from src.utils.logger import logger  # 导入日志模块
from pymysql import MySQLError

class SalesController:
    def __init__(self):
        self.dao = SalesDAO()

    # --- 提交销售逻辑 ---
    def submit_sale(self, sales_id, cust_id, emp_id, remark, items):
        """提交新销售订单"""
        if not items:
            logger.warning(f"销售尝试失败 | 单号: {sales_id} | 原因: 未选择药品")
            return False, "未选择任何药品！"
        
        logger.info(f"正在提交销售结账 | 单号: {sales_id} | 客户: {cust_id} | 经办人: {emp_id}")
        try:
            # 这里的 register_sale 内部会触发：扣减库存、计算总价、更新财务日结
            self.dao.register_sale(sales_id, cust_id, emp_id, remark, items)
            
            logger.info(f"销售结账成功 | 单号: {sales_id} | 项目数: {len(items)}")
            return True, "销售结账成功！"
            
        except MySQLError as e:
            # 重点捕获：tri_sales_reduce_stock 抛出的“库存不足”
            err_msg = e.args[1] if len(e.args) > 1 else str(e)
            logger.warning(f"销售被业务逻辑拦截 | 单号: {sales_id} | 原因: {err_msg}")
            return False, f"销售拦截：{err_msg}"
            
        except Exception as e:
            logger.error(f"销售系统异常 | 单号: {sales_id} | 错误: {e}")
            return False, f"系统错误: {str(e)}"

    # --- 处理退货逻辑 ---
    def process_return(self, return_id, sales_id, emp_id, cust_id, amount, reason, items):
        """处理退货请求"""
        logger.info(f"正在处理退货申请 | 退货单: {return_id} | 原单号: {sales_id}")
        try:
            # 这里的 register_return 内部会触发：回升库存、冲减财务日结
            self.dao.register_return(return_id, sales_id, emp_id, cust_id, amount, reason, items)
            
            logger.info(f"退货处理完成 | 退货单: {return_id} | 金额: {amount}")
            return True, "退货处理完成。"
            
        except MySQLError as e:
            err_msg = e.args[1] if len(e.args) > 1 else str(e)
            logger.warning(f"退货被拦截 | 退货单: {return_id} | 原因: {err_msg}")
            return False, f"退货失败: {err_msg}"
            
        except Exception as e:
            logger.error(f"退货过程发生非预期异常 | 退货单: {return_id} | 错误: {e}")
            return False, str(e)

    # --- 查询相关函数 ---

    def get_history(self):
        """获取所有历史销售主单列表"""
        logger.debug("请求销售历史列表...")
        try:
            data = self.dao.get_sales_history()
            logger.info(f"销售历史加载成功 | 记录数: {len(data)}")
            return True, data
        except Exception as e:
            logger.error(f"销售历史加载失败: {e}")
            return False, str(e)

    def get_order_details(self, sales_id):
        """查看具体某一笔销售单的药品明细"""
        if not sales_id:
            return False, "销售单号不能为空"
            
        logger.debug(f"查询销售明细 | 单号: {sales_id}")
        try:
            details = self.dao.get_sale_details(sales_id)
            if not details:
                logger.warning(f"未找到单号 {sales_id} 的明细记录")
                return False, "未找到该订单的药品明细"
            return True, details
        except Exception as e:
            logger.error(f"查询单号 {sales_id} 明细失败: {e}")
            return False, f"查询明细失败: {str(e)}"
        
    def get_return_history(self):
        """获取所有退货记录"""
        logger.debug("请求退货历史列表...")
        try:
            data = self.dao.get_return_history()
            logger.info(f"退货历史加载成功 | 记录数: {len(data)}")
            return True, data
        except Exception as e:
            logger.error(f"退货历史加载失败: {e}")
            return False, str(e)
        
    def get_return_details(self, return_id):
        """获取某一退货单的明细数据"""
        if not return_id:
            return False, "退货单号不能为空"

        logger.debug(f"查询退货明细 | 退货单: {return_id}")
        try:
            data = self.dao.get_return_details(return_id)
            if not data:
                logger.warning(f"退货单 {return_id} 无明细记录")
                return False, "该退货单没有明细记录"
            return True, data
        except Exception as e:
            logger.error(f"查询退货明细 {return_id} 失败: {e}")
            return False, str(e)