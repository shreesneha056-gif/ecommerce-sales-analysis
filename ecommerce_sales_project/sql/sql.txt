CREATE DATABASE ecommerce_project;

SELECT * FROM ecommerce_sales;

ALTER TABLE ecommerce_sales
DROP COLUMN Column1, Column2, Column3,column11, column12, column13, column14;

SELECT * FROM ecommerce_sales;

---dtpye check
EXEC sp_help 'ecommerce_sales';

---null check

SELECT 
	SUM(IIF(Order_Date IS NULL, 1,0)) AS Order_date_null,
	SUM(IIF(Product_Name = 'NULL' , 1,0)) AS Product_Name_null,
	SUM(IIF(category = 'NULL' , 1,0)) AS Product_Name_null,
	SUM(IIF(Region = 'NULL' , 1,0)) AS Product_Name_null,
	SUM(IIF(Quantity IS NULL, 1,0)) AS Product_Name_null,
	SUM(IIF(Sales IS NULL, 1,0)) AS Product_Name_null,
	SUM(IIF(Profit IS NULL, 1,0)) AS Product_Name_null
FROM ecommerce_sales;


---Auditing the data

SELECT SUM(sales) AS total_sales, SUM(Profit) AS Total_profit,
ROUND(SUM(profit)/SUM(sales),4) AS profit_margin
FROM ecommerce_sales;


CREATE OR ALTER VIEW sales_by_region AS
SELECT TOP 100  region, SUM(sales) AS total_sales_of_product
FROM ecommerce_sales 
GROUP BY region
ORDER BY total_sales_of_product DESC;

SELECT * FROM sales_by_region

CREATE OR ALTER VIEW sales_by_category AS 
SELECT TOP 100 category, SUM(sales) AS total_sales_of_product
FROM ecommerce_sales 
GROUP BY category
ORDER BY total_sales_of_product DESC;

SELECT * FROM sales_by_category

SELECT * FROM ecommerce_sales;

ALTER TABLE ecommerce_sales
ADD 
	YEAR  INT,
	MONTH  INT;

SELECT *FROM ecommerce_sales;

UPDATE ecommerce_sales
SET 
	YEAR = YEAR(Order_Date),
	MONTH = MONTH(Order_Date);

CREATE OR ALTER VIEW monthly_trend AS
SELECT TOP 100 [month], SUM(sales) AS total_sales_of_product
FROM ecommerce_sales 
GROUP BY [month]
ORDER BY total_sales_of_product DESC;

SELECT * FROM monthly_trend

CREATE OR ALTER VIEW yearly_trend AS
SELECT TOP 100 [year], SUM(sales) AS total_sales_of_product
FROM ecommerce_sales 
GROUP BY [year]
ORDER BY total_sales_of_product DESC;

SELECT * FROM yearly_trend;

CREATE OR ALTER VIEW top_products AS
SELECT TOP 100 product_name , SUM(sales) AS total_sales_of_product
FROM ecommerce_sales 
GROUP BY product_name
ORDER BY total_sales_of_product DESC;

SELECT * FROM top_products

CREATE OR ALTER VIEW top_5_products AS
SELECT TOP 5 product_name , SUM(sales) AS total_sales_of_product
FROM ecommerce_sales 
GROUP BY product_name
ORDER BY total_sales_of_product DESC;

SELECT * FROM top_5_products