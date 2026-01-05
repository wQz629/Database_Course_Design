-- =========================================
-- 医药销售管理系统：触发器脚本
-- 说明：本脚本用于触发器的创建，用于对数据的完整性进行校验，并在触发器触发时给出报错提示
-- 适用环境：MySQL 8.0+
-- =========================================

DELIMITER //

-- -------------------------
-- 1. 供应商存在性校验
-- 需求：插入入库单时，若供应商不存在，直接报错
-- -------------------------
CREATE TRIGGER tri_check_supplier_exists
BEFORE INSERT ON purchase_order
FOR EACH ROW
BEGIN
    DECLARE cnt INT;
    SELECT COUNT(*) INTO cnt FROM supplier WHERE supp_id = NEW.supp_id;
    IF cnt = 0 THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = '错误：供应商ID不存在，请先在供应商管理模块进行登记！';
    END IF;
END //


-- -------------------------
-- 2. 进货药品存在性校验
-- 需求：插入入库明细时，若药品不存在，直接报错
-- -------------------------
CREATE TRIGGER tri_check_medicine_exists_purchase
BEFORE INSERT ON purchase_detail
FOR EACH ROW
BEGIN
    DECLARE cnt INT;
    SELECT COUNT(*) INTO cnt FROM medicine WHERE medicine_id = NEW.medicine_id;
    IF cnt = 0 THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = '错误：药品ID不存在，请先在药品信息模块录入该药品！';
    END IF;
END //


-- -------------------------
-- 3. 进货自动增加库存
-- 需求：入库明细插入后，自动更新库存表
-- 逻辑：若inventory没有该药记录则初始化，若有则累加
-- -------------------------
CREATE TRIGGER tri_purchase_add_stock
AFTER INSERT ON purchase_detail
FOR EACH ROW
BEGIN
    -- 检查库存表中是否已有该药记录
    IF EXISTS (SELECT 1 FROM inventory WHERE medicine_id = NEW.medicine_id) THEN
        UPDATE inventory 
        SET stock_quantity = stock_quantity + NEW.quantity
        WHERE medicine_id = NEW.medicine_id;
    ELSE
        -- 若medicine表中已存在（已通过T2校验），但库存表还没记录，则新建
        INSERT INTO inventory (medicine_id, stock_quantity)
        VALUES (NEW.medicine_id, NEW.quantity);
    END IF;
END //


-- -------------------------
-- 4. 客户存在性校验
-- 需求：销售下单时，若客户不存在，报错提示
-- -------------------------
CREATE TRIGGER tri_check_customer_exists
BEFORE INSERT ON sales_order
FOR EACH ROW
BEGIN
    DECLARE cnt INT;
    SELECT COUNT(*) INTO cnt FROM customer WHERE cust_id = NEW.cust_id;
    IF cnt = 0 THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = '错误：该客户不存在（散客请先建档或使用通用客户ID）！';
    END IF;
END //


-- -------------------------
-- 5. 销售扣减库存与超卖检查
-- 需求：销售时检查库存，不足则拦截并报错
-- -------------------------
CREATE TRIGGER tri_sales_reduce_stock
BEFORE INSERT ON sales_detail
FOR EACH ROW
BEGIN
    DECLARE current_stock INT DEFAULT 0;
    
    -- 获取当前库存数量
    SELECT stock_quantity INTO current_stock 
    FROM inventory 
    WHERE medicine_id = NEW.medicine_id;
    
    -- 判断库存（如果没有库存记录或者数量不够）
    IF current_stock IS NULL OR current_stock < NEW.quantity THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = '库存不足：该药品当前库存无法满足本次销售数量！';
    ELSE
        UPDATE inventory 
        SET stock_quantity = stock_quantity - NEW.quantity
        WHERE medicine_id = NEW.medicine_id;
    END IF;
END //


-- -------------------------
-- 6. 退货自动增加库存
-- 需求：退货记录产生后，药库数量回升
-- -------------------------
CREATE TRIGGER tri_return_add_stock
AFTER INSERT ON sales_return_detail
FOR EACH ROW
BEGIN
    UPDATE inventory 
    SET stock_quantity = stock_quantity + NEW.return_quantity
    WHERE medicine_id = NEW.medicine_id;
END //


-- -------------------------
-- 7. 销售订单汇总统计
-- 需求：每成一笔单，自动在日汇总表累加金额和单数
-- -------------------------
CREATE TRIGGER tri_sales_daily_update
AFTER INSERT ON sales_order
FOR EACH ROW
BEGIN
    INSERT INTO sales_daily_summary (summary_date, total_sales_amount, net_amount, order_count)
    VALUES (DATE(NEW.sales_date), NEW.total_amount, NEW.total_amount, 1)
    ON DUPLICATE KEY UPDATE
        total_sales_amount = total_sales_amount + NEW.total_amount,
        net_amount = net_amount + NEW.total_amount,
        order_count = order_count + 1;
END //


-- -------------------------
-- 8. 退货汇总统计
-- 需求：每发生退货，更新当日退货额和净额
-- -------------------------
CREATE TRIGGER tri_return_daily_update
AFTER INSERT ON sales_return
FOR EACH ROW
BEGIN
    INSERT INTO sales_daily_summary (summary_date, total_return_amount, net_amount)
    VALUES (DATE(NEW.return_date), 0.00, 0.00) -- 初始化当日记录（如果销售还没产生就有退货的话）
    ON DUPLICATE KEY UPDATE
        total_return_amount = total_return_amount + NEW.total_amount,
        net_amount = net_amount - NEW.total_amount;
END //


-- -------------------------
-- 9. 自动计算入库单总价
-- 逻辑：用户只需插入明细，主表的total_amount会自动累加，防止人工计算错误
-- -------------------------
CREATE TRIGGER tri_calc_purchase_total
AFTER INSERT ON purchase_detail
FOR EACH ROW
BEGIN
    UPDATE purchase_order 
    SET total_amount = (SELECT SUM(quantity * unit_price) FROM purchase_detail WHERE order_id = NEW.order_id)
    WHERE order_id = NEW.order_id;
END //


-- -------------------------
-- 10. 自动计算销售单总价
-- 逻辑：根据销售明细自动更新销售主单总金额
-- -------------------------
CREATE TRIGGER tri_calc_sales_total
AFTER INSERT ON sales_detail
FOR EACH ROW
BEGIN
    UPDATE sales_order 
    SET total_amount = (SELECT SUM(quantity * unit_price) FROM sales_detail WHERE sales_id = NEW.sales_id)
    WHERE sales_id = NEW.sales_id;
END //

DELIMITER ;