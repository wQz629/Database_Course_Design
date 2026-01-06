-- ========================================================
-- 医药销售管理系统：测试数据
-- 说明：运行前请确保已执行建表和触发器脚本
-- ========================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0; 

-- 1. 清理历史数据
TRUNCATE TABLE sales_daily_summary;
TRUNCATE TABLE sales_return_detail;
TRUNCATE TABLE sales_return;
TRUNCATE TABLE sales_detail;
TRUNCATE TABLE sales_order;
TRUNCATE TABLE inventory;
TRUNCATE TABLE purchase_detail;
TRUNCATE TABLE purchase_order;
TRUNCATE TABLE medicine;
TRUNCATE TABLE supplier;
TRUNCATE TABLE customer;
TRUNCATE TABLE employee;

SET FOREIGN_KEY_CHECKS = 1;

-- --------------------------------------------------------
-- 2. 基础信息初始化
-- --------------------------------------------------------

-- 插入员工 (店长、销售、库管)
INSERT INTO employee VALUES 
('E0001', '张三', 'M', '13800138001', '店长'),
('E0002', '李红', 'F', '13800138002', '销售员'),
('E0003', '王伟', 'M', '13800138003', '仓库管理员');

-- 插入供应商
INSERT INTO supplier VALUES 
('S000000001', '华东医药集团', '陈经理', '18611110001', '上海市', '6222021001010001'),
('S000000002', '广药白云山', '林主任', '18611110002', '广州市', '6222021001010002'),
('S000000005', '云南白药', '王经理', '18611110005', '昆明市', '6222021001010005');

-- 插入客户
INSERT INTO customer VALUES 
('C000000001', '赵先生', '13911112222', '北京市朝阳区'),
('C000000002', '钱女士', '13922223333', '上海市黄浦区'),
('C000000010', '通用散客', '13000000000', '门店柜台');

-- 插入药品信息
INSERT INTO medicine VALUES 
('M000000001', '阿莫西林胶囊', '抗生素', '0.25g*24粒', '广药白云山', '2025-01-01', '2026-12-31', 15.50, '感冒消炎用'),
('M000000002', '布洛芬缓释胶囊', '解热镇痛', '0.3g*22粒', '中美史克', '2025-05-10', '2027-05-09', 28.00, '止痛退烧'),
('M000000003', '板蓝根颗粒', '中成药', '10g*20袋', '华东医药', '2025-06-01', '2027-05-31', 12.00, '清热解毒'),
('M000000004', '云南白药喷雾', '外用', '85g+30g', '云南白药', '2025-02-01', '2028-01-31', 45.00, '跌打损伤');


-- --------------------------------------------------------
-- 3. 模拟进货流程 (填充库存)
-- --------------------------------------------------------

-- 1月1日：从广药进货阿莫西林
INSERT INTO purchase_order (order_id, supp_id, emp_id, order_date, total_amount, invoice_number, remark)
VALUES ('PO26010101', 'S000000002', 'E0003', '2026-01-01 10:00:00', 0, 'FP20260001', '首批入库');
INSERT INTO purchase_detail VALUES ('PO26010101', 'M000000001', 200, 8.50); -- 成本8.5，卖15.5

-- 1月2日：进货布洛芬和板蓝根
INSERT INTO purchase_order (order_id, supp_id, emp_id, order_date, total_amount, invoice_number, remark)
VALUES ('PO26010201', 'S000000001', 'E0003', '2026-01-02 14:30:00', 0, 'FP20260002', '补货');
INSERT INTO purchase_detail VALUES ('PO26010201', 'M000000002', 100, 15.00);
INSERT INTO purchase_detail VALUES ('PO26010201', 'M000000003', 50, 6.00);


-- --------------------------------------------------------
-- 4. 模拟销售流程 (生成财务数据)
-- --------------------------------------------------------

-- 1月3日：赵先生买药
INSERT INTO sales_order (sales_id, cust_id, emp_id, sales_date, total_amount, remark)
VALUES ('SO26010301', 'C000000001', 'E0002', '2026-01-03 09:00:00', 0, '零售');
INSERT INTO sales_detail VALUES ('SO26010301', 'M000000001', 2, 15.50);
INSERT INTO sales_detail VALUES ('SO26010301', 'M000000002', 1, 28.00);

-- 1月4日：多笔销售（测试日汇总累加）
-- 订单 A
INSERT INTO sales_order (sales_id, cust_id, emp_id, sales_date, total_amount, remark)
VALUES ('SO26010401', 'C000000002', 'E0002', '2026-01-04 11:00:00', 0, '零售');
INSERT INTO sales_detail VALUES ('SO26010401', 'M000000003', 10, 12.00);

-- 订单 B
INSERT INTO sales_order (sales_id, cust_id, emp_id, sales_date, total_amount, remark)
VALUES ('SO26010402', 'C000000010', 'E0002', '2026-01-04 15:00:00', 0, '散客');
INSERT INTO sales_detail VALUES ('SO26010402', 'M000000001', 5, 15.50);


-- --------------------------------------------------------
-- 5. 模拟退货流程 (验证逻辑)
-- --------------------------------------------------------

-- 1月5日：客户退回 1月4日的板蓝根 2 袋
INSERT INTO sales_return (return_id, sales_id, emp_id, cust_id, return_date, total_amount, reason)
VALUES ('RE26010501', 'SO26010401', 'E0002', 'C000000002', '2026-01-05 10:00:00', 24.00, '包装破损');
INSERT INTO sales_return_detail VALUES ('RE26010501', 'M000000003', 2);


-- --------------------------------------------------------
-- 演示数据注入完毕！
-- --------------------------------------------------------