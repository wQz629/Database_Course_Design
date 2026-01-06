-- =========================================
-- 医药销售管理系统：全量建表 SQL（MySQL 8.0+）
-- Engine: InnoDB, Charset: utf8mb4
-- =========================================

-- 建立一个数据库
DROP DATABASE IF EXISTS medicine_sales_management_system;
CREATE DATABASE IF NOT EXISTS medicine_sales_management_system;
USE medicine_sales_management_system;

-- 设置数据库字符集为 utf8mb4
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- -------------------------
-- 1. 基础信息管理
-- -------------------------

DROP TABLE IF EXISTS sales_daily_summary;
DROP TABLE IF EXISTS sales_return_detail;
DROP TABLE IF EXISTS sales_return;
DROP TABLE IF EXISTS sales_detail;
DROP TABLE IF EXISTS sales_order;

DROP TABLE IF EXISTS inventory;

DROP TABLE IF EXISTS purchase_detail;
DROP TABLE IF EXISTS purchase_order;

DROP TABLE IF EXISTS supplier;
DROP TABLE IF EXISTS customer;
DROP TABLE IF EXISTS employee;
DROP TABLE IF EXISTS medicine;

-- 药品信息表
CREATE TABLE medicine (
  medicine_id     CHAR(10)     NOT NULL COMMENT '药品ID（唯一标识）',
  medicine_name   VARCHAR(50)  NOT NULL COMMENT '药品通用名',
  category        VARCHAR(50)  NOT NULL COMMENT '药品分类',
  specification   VARCHAR(50)  NOT NULL COMMENT '规格（如：1g*24片）',
  manufacturer    VARCHAR(50)  NOT NULL COMMENT '生产厂家',
  production_date DATE         NOT NULL COMMENT '生产日期',
  expiry_date     DATE         NOT NULL COMMENT '有效期至',
  retail_price    DECIMAL(10,2) NOT NULL COMMENT '零售单价',
  description     VARCHAR(200) DEFAULT NULL COMMENT '药品说明',
  PRIMARY KEY (medicine_id),
  CHECK (retail_price >= 0),
  CHECK (expiry_date >= production_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 员工信息表
CREATE TABLE employee (
  emp_id    CHAR(5)      NOT NULL COMMENT '员工ID',
  emp_name  VARCHAR(10)  NOT NULL COMMENT '员工名字',
  gender    CHAR(1)      NOT NULL COMMENT '性别（M/F）',
  phone     CHAR(11)     NOT NULL COMMENT '联系电话',
  position  VARCHAR(20)  NOT NULL COMMENT '职位',
  PRIMARY KEY (emp_id),
  CHECK (gender IN ('M','F'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 客户信息表
CREATE TABLE customer (
  cust_id   CHAR(10)     NOT NULL COMMENT '客户ID',
  cust_name VARCHAR(10)  NOT NULL COMMENT '客户姓名',
  phone     CHAR(11)     NOT NULL COMMENT '联系电话',
  address   VARCHAR(50)  NOT NULL COMMENT '地址',
  PRIMARY KEY (cust_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 供应商信息表
CREATE TABLE supplier (
  supp_id        CHAR(10)     NOT NULL COMMENT '供应商ID',
  supp_name      VARCHAR(30)  NOT NULL COMMENT '供应商名称',
  contact_person VARCHAR(10)  NOT NULL COMMENT '联系人',
  phone          CHAR(11)     NOT NULL COMMENT '联系电话',
  address        VARCHAR(50)  NOT NULL COMMENT '地址',
  account        CHAR(16)     NOT NULL COMMENT '银行账户',
  PRIMARY KEY (supp_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- -------------------------
-- 2. 进货管理
-- -------------------------

-- 入库登记表（入库单）
CREATE TABLE purchase_order (
  order_id        CHAR(10)      NOT NULL COMMENT '入库单号',
  supp_id         CHAR(10)      NOT NULL COMMENT '供应商ID',
  emp_id          CHAR(5)       NOT NULL COMMENT '操作员ID',
  order_date      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '入库日期时间',
  total_amount    DECIMAL(12,2) NOT NULL COMMENT '入库单总金额',
  invoice_number  CHAR(20)      NOT NULL COMMENT '发票号',
  remark          VARCHAR(100)  DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (order_id),
  CONSTRAINT fk_po_supplier FOREIGN KEY (supp_id)
    REFERENCES supplier(supp_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_po_employee FOREIGN KEY (emp_id)
    REFERENCES employee(emp_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CHECK (total_amount >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 入库明细表（一个入库单多种药）
CREATE TABLE purchase_detail (
  order_id    CHAR(10)      NOT NULL COMMENT '入库单号',
  medicine_id CHAR(10)      NOT NULL COMMENT '药品ID',
  quantity    INT           NOT NULL COMMENT '入库数量',
  unit_price  DECIMAL(10,2) NOT NULL COMMENT '采购单价',
  PRIMARY KEY (order_id, medicine_id),
  CONSTRAINT fk_pd_order FOREIGN KEY (order_id)
    REFERENCES purchase_order(order_id)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_pd_medicine FOREIGN KEY (medicine_id)
    REFERENCES medicine(medicine_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CHECK (quantity > 0),
  CHECK (unit_price >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- -------------------------
-- 3. 库存管理
-- -------------------------

-- 库存表（每个药品一行库存）
CREATE TABLE inventory (
  medicine_id    CHAR(10) NOT NULL COMMENT '药品ID',
  stock_quantity INT      NOT NULL DEFAULT 0 COMMENT '库存总量',
  PRIMARY KEY (medicine_id),
  CONSTRAINT fk_inv_medicine FOREIGN KEY (medicine_id)
    REFERENCES medicine(medicine_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CHECK (stock_quantity >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -------------------------
-- 4. 销售管理
-- -------------------------

-- 销售登记表（销售单）
CREATE TABLE sales_order (
  sales_id      CHAR(10)      NOT NULL COMMENT '销售单号',
  cust_id       CHAR(10)      NOT NULL COMMENT '客户ID',
  emp_id        CHAR(5)       NOT NULL COMMENT '操作员ID',
  sales_date    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '销售日期',
  total_amount  DECIMAL(12,2) NOT NULL COMMENT '销售总金额',
  remark        VARCHAR(100)  DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (sales_id),
  CONSTRAINT fk_so_customer FOREIGN KEY (cust_id)
    REFERENCES customer(cust_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_so_employee FOREIGN KEY (emp_id)
    REFERENCES employee(emp_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CHECK (total_amount >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 销售明细表（一个销售单多种药）
CREATE TABLE sales_detail (
  sales_id    CHAR(10)      NOT NULL COMMENT '销售单号',
  medicine_id CHAR(10)      NOT NULL COMMENT '药品ID',
  quantity    INT           NOT NULL COMMENT '销售数量',
  unit_price  DECIMAL(10,2) NOT NULL COMMENT '销售单价',
  PRIMARY KEY (sales_id, medicine_id),
  CONSTRAINT fk_sd_sales FOREIGN KEY (sales_id)
    REFERENCES sales_order(sales_id)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_sd_medicine FOREIGN KEY (medicine_id)
    REFERENCES medicine(medicine_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CHECK (quantity > 0),
  CHECK (unit_price >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 销售退货表（退货单）
CREATE TABLE sales_return (
  return_id    CHAR(10)      NOT NULL COMMENT '退货单号',
  sales_id     CHAR(10)      NOT NULL COMMENT '原始销售单号',
  emp_id       CHAR(5)       NOT NULL COMMENT '操作员ID',
  cust_id      CHAR(10)      NOT NULL COMMENT '退货客户',
  return_date  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '退货日期',
  total_amount DECIMAL(12,2) NOT NULL COMMENT '退货总金额',
  reason       VARCHAR(100)  DEFAULT NULL COMMENT '退货原因',
  PRIMARY KEY (return_id),
  CONSTRAINT fk_sr_sales FOREIGN KEY (sales_id)
    REFERENCES sales_order(sales_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_sr_employee FOREIGN KEY (emp_id)
    REFERENCES employee(emp_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_sr_customer FOREIGN KEY (cust_id)
    REFERENCES customer(cust_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CHECK (total_amount >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 销售退货明细表（退货单与药品）
CREATE TABLE sales_return_detail (
  return_id       CHAR(10) NOT NULL COMMENT '退货单号',
  medicine_id     CHAR(10) NOT NULL COMMENT '药品ID',
  return_quantity INT      NOT NULL COMMENT '退货数量',
  PRIMARY KEY (return_id, medicine_id),
  CONSTRAINT fk_srd_return FOREIGN KEY (return_id)
    REFERENCES sales_return(return_id)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_srd_medicine FOREIGN KEY (medicine_id)
    REFERENCES medicine(medicine_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CHECK (return_quantity > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- -------------------------
-- 5. 财务统计
-- -------------------------

-- 日销售汇总表
CREATE TABLE sales_daily_summary (
  summary_date        DATE         NOT NULL COMMENT '统计日期',
  total_sales_amount  DECIMAL(12,2) NOT NULL DEFAULT 0.00 COMMENT '当日销售总额',
  total_return_amount DECIMAL(12,2) NOT NULL DEFAULT 0.00 COMMENT '当日退货总额',
  net_amount          DECIMAL(12,2) NOT NULL DEFAULT 0.00 COMMENT '当日净额',
  order_count         INT          NOT NULL DEFAULT 0 COMMENT '当日销售单数',
  PRIMARY KEY (summary_date),
  CHECK (total_sales_amount >= 0),
  CHECK (total_return_amount >= 0),
  CHECK (order_count >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

SET FOREIGN_KEY_CHECKS = 1;
