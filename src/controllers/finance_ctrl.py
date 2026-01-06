# src/controllers/finance_ctrl.py
from src.database.dao import FinanceDAO
from src.utils.logger import logger  

class FinanceController:
    def __init__(self):
        self.dao = FinanceDAO()

    def get_daily_logs(self):
        """获取日销售统计流水"""
        logger.debug("正在请求日销售统计流水数据...")
        try:
            data = self.dao.get_daily_summaries()
            logger.info(f"成功获取日统计数据，共 {len(data)} 条记录")
            return True, data
        except Exception as e:
            logger.error(f"获取日统计流水失败: {e}")
            return False, str(e)

    def get_monthly_summary(self, year, month):
        """获取月度统计数据"""
        logger.info(f"正在生成月度经营报表: {year}年{month}月")
        try:
            data = self.dao.get_monthly_report(year, month)
            
            # 处理当月无数据的情况
            if not data or data.get('month_sales') is None:
                logger.warning(f"{year}-{month} 期间未找到任何交易记录")
                data = {
                    "month_sales": 0, 
                    "month_return": 0, 
                    "month_net": 0, 
                    "month_orders": 0
                }
            else:
                logger.info(
                    f"月度报表生成成功 | 销售额: {data['month_sales']} | "
                    f"净额: {data['month_net']} | 订单数: {data['month_orders']}"
                )
                
            return True, data
        except Exception as e:
            logger.error(f"生成 {year}-{month} 月度报表时发生异常: {e}")
            return False, str(e)