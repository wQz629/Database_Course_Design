DROP TRIGGER IF EXISTS trg_purchase_add_inventory;

CREATE TRIGGER trg_purchase_add_inventory
AFTER INSERT ON purchase_detail
FOR EACH ROW
INSERT INTO inventory (medicine_id, stock_quantity)
VALUES (NEW.medicine_id, NEW.quantity)
ON DUPLICATE KEY UPDATE stock_quantity = stock_quantity + NEW.quantity;

DROP TRIGGER IF EXISTS trg_sales_reduce_inventory;

CREATE TRIGGER trg_sales_reduce_inventory
AFTER INSERT ON sales_detail
FOR EACH ROW
UPDATE inventory
SET stock_quantity = stock_quantity - NEW.quantity
WHERE medicine_id = NEW.medicine_id;

DROP TRIGGER IF EXISTS trg_sales_daily_summary_insert;

CREATE TRIGGER trg_sales_daily_summary_insert
AFTER INSERT ON sales_order
FOR EACH ROW
INSERT INTO sales_daily_summary
  (summary_date, total_sales_amount, net_amount, order_count)
VALUES
  (DATE(NEW.sales_date), NEW.total_amount, NEW.total_amount, 1)
ON DUPLICATE KEY UPDATE
  total_sales_amount = total_sales_amount + NEW.total_amount,
  net_amount         = net_amount + NEW.total_amount,
  order_count        = order_count + 1;

DROP TRIGGER IF EXISTS trg_return_daily_summary_insert;

CREATE TRIGGER trg_return_daily_summary_insert
AFTER INSERT ON sales_return
FOR EACH ROW
INSERT INTO sales_daily_summary
  (summary_date, total_return_amount, net_amount)
VALUES
  (DATE(NEW.return_date), NEW.total_amount, -NEW.total_amount)
ON DUPLICATE KEY UPDATE
  total_return_amount = total_return_amount + NEW.total_amount,
  net_amount          = net_amount - NEW.total_amount;

