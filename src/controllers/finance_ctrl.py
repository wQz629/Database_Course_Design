# src/controllers/finance_ctrl.py
from src.database.dao import FinanceDAO

class FinanceController:
    def __init__(self):
        self.dao = FinanceDAO()

    def get_daily_logs(self):
        return self.dao.get_daily_summaries()

    def get_monthly_summary(self, year, month):
        data = self.dao.get_monthly_report(year, month)
        # 逻辑处理：如果当月没数据，返回全0字典避免 UI 报错
        if not data or data['month_sales'] is None:
            return {
                "month_sales": 0, "month_return": 0, 
                "month_net": 0, "month_orders": 0
            }
        return data