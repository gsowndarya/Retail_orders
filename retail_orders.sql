use retail_orders;  

select * from df1;
select * from df2;

-- concat table

CREATE TABLE df3 AS
SELECT COALESCE(df1.order_id, df2.order_id) AS order_id, df1.order_date, df1.ship_mode, df1.segment, 
df1.country, df1.city, df1.state, df1.postal_code, df1.region, 
df2.category, df2.sub_category, df2.product_id, df2.cost_price, df2.list_price, df2.quantity, 
df2.discount_percent, df2.discount, df2.sale_price, df2.profit
FROM df1
LEFT JOIN df2 ON df1.order_id = df2.order_id
UNION
SELECT COALESCE(df1.order_id, df2.order_id) AS order_id, df1.order_date, df1.ship_mode, df1.segment, 
df1.country, df1.city, df1.state, df1.postal_code, df1.region, 
df2.category, df2.sub_category, df2.product_id, df2.cost_price, df2.list_price, df2.quantity, 
df2.discount_percent, df2.discount, df2.sale_price, df2.profit
FROM df1
RIGHT JOIN df2 ON df1.order_id = df2.order_id;


select * from df3

-- Top-Selling Products.
-- Identify the products that generate the highest revenue based on sale prices.

select category,sub_category, round(sum(sale_price*quantity),2)as revenue from df2
group by category,sub_category
order by revenue desc;


-- Monthly Sales Analysis. 
-- Compare year-over-year sales to identify growth or decline in certain months.

SELECT * 
FROM (
    SELECT 
        EXTRACT(YEAR FROM order_date) AS year,
        EXTRACT(MONTH FROM order_date) AS month,
        ROUND(SUM(sale_price * quantity), 2) AS total_sales,
        LAG(ROUND(SUM(sale_price * quantity), 2)) OVER (
            PARTITION BY EXTRACT(MONTH FROM order_date) 
            ORDER BY EXTRACT(YEAR FROM order_date)
        ) AS previous_sales,
        ROUND(
			((SUM(sale_price * quantity) - 
			LAG(SUM(sale_price * quantity)) OVER (
				PARTITION BY EXTRACT(MONTH FROM order_date) 
				ORDER BY EXTRACT(YEAR FROM order_date)
			)) / NULLIF(LAG(SUM(sale_price * quantity)) OVER (
				PARTITION BY EXTRACT(MONTH FROM order_date) 
				ORDER BY EXTRACT(YEAR FROM order_date)
			), 0)) * 100,2) AS year_growth
    FROM df3
    GROUP BY year, month
) AS yearsales
WHERE year = 2023
ORDER BY month, year;


-- Product Performance.
-- Use functions like GROUP BY, HAVING, ROW_NUMBER(), and CASE WHEN to categorize and rank products by their revenue,
-- profit margin, etc.

SELECT 
	product_id,
	sub_category,
	category,
	ROUND(SUM(sale_price * quantity), 2) AS total_revenue,
	ROUND(SUM(profit), 2) AS total_profit,
    ROUND((SUM(profit) / NULLIF(SUM(sale_price * quantity), 0)) * 100, 2) AS profit_margin,
    ROW_NUMBER() OVER (ORDER BY SUM(sale_price * quantity) DESC) AS revenue_rank,
    CASE 
        WHEN SUM(sale_price * quantity) >= 100000 THEN 'High Performer'
        WHEN SUM(sale_price * quantity) BETWEEN 50000 AND 99999 THEN 'Medium Performer'
        ELSE 'Low Performer'
    END AS performance_category
    FROM df3
    GROUP BY product_id, sub_category, category
    HAVING SUM(sale_price * quantity) > 10000  


-- Regional Sales Analysis.
-- Query sales data by region to identify which areas are performing best.

SELECT 
region, 
ROUND(SUM(sale_price * quantity),2) AS total_revenue,
ROUND(SUM(profit),2) AS total_profit, 
COUNT(DISTINCT order_id) AS order_count FROM df3
GROUP BY region
ORDER BY total_revenue DESC;


-- Discount Analysis.
-- Identify products with discounts greater than 20% and calculate the impact of discounts on sales.

WITH DiscountedProducts AS (
    SELECT 
        sub_category,
        category,
        ROUND(AVG(discount_percent) * 100, 2) AS avg_discount_percentage,
        SUM(quantity) AS total_quantity_sold,
        ROUND(SUM(sale_price * quantity), 2) AS total_revenue,
        ROUND(SUM(discount), 2) AS total_discount_amount,
        ROUND(SUM(profit), 2) AS total_profit,
        ROUND((SUM(profit) / NULLIF(SUM(sale_price * quantity), 0)) * 100, 2) AS profit_margin
    FROM df3
    WHERE discount_percent > 0.20 
    GROUP BY sub_category, category
)
SELECT 
    *,
    ROUND((total_discount_amount / NULLIF(total_revenue, 0)) * 100, 2) AS discount_impact_on_sales
FROM DiscountedProducts
ORDER BY avg_discount_percentage DESC, total_revenue DESC;



-- 1. Find top 10 highest revenue generating products.
-- Identifies best-selling products that drive the most revenue.

SELECT b.category,b.sub_category,a.product_id,  ROUND(SUM(a.sale_price * a.quantity), 2) AS revenue FROM df3 a
JOIN df2 b ON a.order_id = b.order_id
GROUP BY b.category, b.sub_category, a.product_id
ORDER BY revenue DESC
LIMIT 10;

-- 2. Find the top 5 cities with the highest profit margins.
-- Helps understand which cities yield the highest profit margins.

SELECT b.city, ROUND((SUM(a.profit) / SUM(a.sale_price * a.quantity)) * 100, 2) AS profit_margin FROM df3 a
JOIN df1 b ON a.order_id = b.order_id
GROUP BY b.city
ORDER BY profit_margin DESC
LIMIT 5;


-- 3. Calculate the total discount given for each category
-- Reveals which product categories receive the highest total discounts.

SELECT category,sub_category,product_id, ROUND(SUM(discount),2) AS total_discount FROM df3
GROUP BY category,sub_category,product_id
ORDER BY total_discount DESC;


-- 4. Find the average sale price per product category.
-- Helps in pricing strategy and competitive analysis.

SELECT category, ROUND(AVG(sale_price),2) AS avg_sale_price FROM df3
GROUP BY category
ORDER BY avg_sale_price DESC;


-- 5. Find the region with the highest average sale price. 
-- Determines which regions sell higher-value products.

SELECT region, ROUND(AVG(sale_price),2) AS avg_sale_price FROM df3
GROUP BY region
ORDER BY avg_sale_price DESC
;


-- 6. Find the total profit per category.
-- Identifies the most profitable product categories.

SELECT category,ROUND(SUM(profit),2) AS total_profit FROM df3
GROUP BY category
ORDER BY total_profit;


-- 7. Identify the top 3 segments with the highest quantity of orders.
-- Highlights which customer segments order the most.

SELECT segment, SUM(quantity) AS total_quantity FROM df3
GROUP BY segment
ORDER BY total_quantity DESC
LIMIT 3;


-- 8. Determine the average discount percentage given per region.
-- Analyzes regional discounting strategies.

SELECT region, CONCAT(ROUND(AVG(discount_percent), 2), "%") AS avg_discount_percent FROM df3
GROUP BY region
ORDER BY avg_discount_percent DESC;


-- 9. Find the product category with the highest total profit.
-- Identifies the most profitable category.

SELECT category,ROUND(SUM(profit)) AS total_profit FROM df3
GROUP BY category
ORDER BY total_profit DESC
LIMIT 1;


-- 10. Calculate the total revenue generated per year.
-- Helps track revenue trends year-over-year.

SELECT YEAR(order_date) AS year, ROUND(SUM(sale_price * quantity),2) AS total_revenue FROM df3
GROUP BY YEAR(order_date)
ORDER BY year ASC;


-- 11. Identify the Regions With the Highest Repeat Orders
-- Identifies which regions have the most repeat customers.

SELECT region, 
       COUNT(DISTINCT order_id) AS total_orders, 
       COUNT(order_id) - COUNT(DISTINCT order_id) AS repeat_orders
FROM df3
GROUP BY region
ORDER BY repeat_orders DESC
LIMIT 5;


--  12. Determine the Impact of Discounts on Profitability
--  Helps analyze whether higher discounts lead to lower profitability.

SELECT 
    CASE 
        WHEN discount_percent > 0.20 THEN 'High Discount (>20%)'
        ELSE 'Low Discount (≤20%)'
    END AS discount_category,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(SUM(sale_price * quantity), 2) AS total_revenue,
    ROUND((SUM(profit) / NULLIF(SUM(sale_price * quantity), 0)) * 100, 2) AS profit_margin
FROM df3 
GROUP BY discount_category;


-- 13. Find the Average Order Value (AOV) Per Segment
-- Helps in understanding the purchasing power of different segments.

SELECT segment, 
       ROUND(SUM(sale_price * quantity) / COUNT(DISTINCT order_id), 2) AS avg_order_value
FROM df3 
GROUP BY segment
ORDER BY avg_order_value DESC;


-- 14. Identify the Products With the Highest Order Frequency
-- Identifies products that are ordered most frequently.

SELECT a.product_id, b.sub_category, b.category, 
       COUNT(DISTINCT a.order_id) AS order_count
FROM df3 a
JOIN df2 b ON a.product_id = b.product_id
GROUP BY a.product_id, b.sub_category, b.category
ORDER BY order_count DESC
LIMIT 10;
 
 
-- 15. Find the Number of Orders Per Region
-- Helps analyze which regions have the most orders.

SELECT region, COUNT(DISTINCT order_id) AS order_count
FROM df3 
GROUP BY region
ORDER BY order_count DESC;


-- 16. Find the Month With the Highest Sales
-- Helps in identifying seasonal sales trends

SELECT EXTRACT(YEAR FROM order_date) AS year, 
       EXTRACT(MONTH FROM order_date) AS month, 
       ROUND(SUM(sale_price * quantity), 2) AS total_sales
FROM df3 
GROUP BY year, month
ORDER BY total_sales DESC;


-- 17. Identify the Top 3 States With the Highest Revenue
--  Helps determine which states contribute most to revenue.

SELECT state, 
ROUND(SUM(sale_price * quantity), 2) AS total_revenue
FROM df3 
GROUP BY state
ORDER BY total_revenue DESC
LIMIT 5;


-- 18. Calculate the Profit Margin Per Category
-- Helps determine which product categories have the best profitability.

SELECT b.category, 
       ROUND(SUM(a.profit) / NULLIF(SUM(a.sale_price * a.quantity), 0) * 100, 2) AS profit_margin
FROM df3 a
JOIN df2 b ON a.product_id = b.product_id
GROUP BY b.category
ORDER BY profit_margin DESC;


-- 19.Identify the Most Discounted Products
--  Identifies products that receive the highest average discounts.

SELECT a.product_id, b.sub_category, b.category, 
       ROUND(AVG(a.discount_percent) * 100, 2) AS avg_discount_percentage
FROM df3 a
JOIN df2 b ON a.product_id = b.product_id
GROUP BY a.product_id, b.sub_category, b.category
ORDER BY avg_discount_percentage DESC;


-- 20. Identify the highest revenue-generating segment
-- Helps identify which segments bring the most revenue

SELECT segment, 
ROUND(SUM(sale_price * quantity), 2) AS total_revenue
FROM df3 
GROUP BY segment
ORDER BY total_revenue DESC
LIMIT 1;

-- 21. Query sales data by region to identify which areas are performing best.
-- Helps to identify which areas are performing best.  

SELECT 
region, 
ROUND(SUM(sale_price * quantity),2) AS total_revenue,
ROUND(SUM(profit),2) AS total_profit, 
COUNT(DISTINCT order_id) AS order_count FROM df3
GROUP BY region
ORDER BY total_revenue DESC;

-- 22.Compare year-over-year sales to identify growth or decline in certain months
-- Helps to identify the growth in year over year(month) sales trends

SELECT * 
FROM (
    SELECT 
        EXTRACT(YEAR FROM order_date) AS year,
        EXTRACT(MONTH FROM order_date) AS month,
        ROUND(SUM(sale_price * quantity), 2) AS total_sales,
        LAG(ROUND(SUM(sale_price * quantity), 2)) OVER (
            PARTITION BY EXTRACT(MONTH FROM order_date) 
            ORDER BY EXTRACT(YEAR FROM order_date)
        ) AS previous_sales,
        ROUND(
			((SUM(sale_price * quantity) - 
			LAG(SUM(sale_price * quantity)) OVER (
				PARTITION BY EXTRACT(MONTH FROM order_date) 
				ORDER BY EXTRACT(YEAR FROM order_date)
			)) / NULLIF(LAG(SUM(sale_price * quantity)) OVER (
				PARTITION BY EXTRACT(MONTH FROM order_date) 
				ORDER BY EXTRACT(YEAR FROM order_date)
			), 0)) * 100,2) AS year_growth
    FROM df3
    GROUP BY year, month
) AS yearsales
WHERE year = 2023
ORDER BY month, year;


-- joins (outer => left + union + right)

select * from df1
left join  df2
on df1.order_id = df2.order_id 
union
select * from df1
right join  df2
on df1.order_id = df2.order_id










