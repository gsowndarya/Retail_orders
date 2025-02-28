import streamlit as st
import pandas as pd
import pymysql  
import plotly.express as px
import plotly.graph_objects as go

# MySQL Connection
myconnection = pymysql.connect(
    host='127.0.0.1',
    user='root',
    passwd='11111',
    database='retail_orders'
)  
cursor = myconnection.cursor()

# Streamlit UI
st.set_page_config(page_title="Retail Order Data Analysis", layout="wide")
st.title("📊 Retail Order Data Analysis")

# Dropdown for  query selection
query_options = {
    "1.Find top 10 highest revenue generating products": """
        SELECT b.category,b.sub_category,a.product_id,  ROUND(SUM(a.sale_price * a.quantity), 2) AS revenue FROM df3 a
        JOIN df2 b ON a.order_id = b.order_id
        GROUP BY b.category, b.sub_category, a.product_id
        ORDER BY revenue DESC
        LIMIT 10;
    """,
    "2.Find the top 5 cities with the highest profit margins": """
        SELECT b.city, ROUND((SUM(a.profit) / SUM(a.sale_price * a.quantity)) * 100, 2) AS profit_margin FROM df3 a
        JOIN df1 b ON a.order_id = b.order_id
        GROUP BY b.city
        ORDER BY profit_margin DESC
        LIMIT 5;
    """,
    "3.Calculate the total discount given for each category": """
        SELECT category, 
        ROUND(SUM(discount),2) AS total_discount FROM df3
        GROUP BY category
        ORDER BY total_discount DESC;
    """,
    "4.Find the average sale price per product category": """
        SELECT category, 
        ROUND(AVG(sale_price),2) AS avg_sale_price FROM df3
        GROUP BY category
        ORDER BY avg_sale_price DESC;
    """,
    "5.Find the region with the highest average sale price":"""
        SELECT region, 
        ROUND(AVG(sale_price),2) AS avg_sale_price FROM df3
        GROUP BY region
        ORDER BY avg_sale_price DESC;
    """,
    "6.Find the total profit per category": """ 
        SELECT category,
        ROUND(SUM(profit),2) AS total_profit FROM df3
        GROUP BY category
        ORDER BY total_profit;
    """,
    "7.Identify the top 3 segments with the highest quantity of orders.": """
        SELECT segment, 
        SUM(quantity) AS total_quantity FROM df3
        GROUP BY segment
        ORDER BY total_quantity DESC
        LIMIT 3;
    """,
    "8.Determine the average discount percentage given per region": """
        SELECT region, 
        CONCAT(ROUND(AVG(discount_percent), 2), "%") AS avg_discount_percent FROM df3
        GROUP BY region
        ORDER BY avg_discount_percent DESC;
    """,
    "9.Find the product category with the highest total profit":"""
        SELECT category,
        ROUND(SUM(profit)) AS total_profit FROM df3
        GROUP BY category
        ORDER BY total_profit DESC;
    """,
    "10.Calculate the total revenue generated per year":"""
        SELECT YEAR(order_date) AS year, 
        ROUND(SUM(sale_price * quantity),2) AS total_revenue FROM df3
        GROUP BY YEAR(order_date)
        ORDER BY year ASC;
    """,
    
    "11.Identify the Regions With the Highest Repeat Orders": """
        SELECT region, 
        COUNT(DISTINCT order_id) AS total_orders, 
        COUNT(order_id) - COUNT(DISTINCT order_id) AS repeat_orders
        FROM df3
        GROUP BY region
        ORDER BY repeat_orders DESC;
    """,
    "12.Determine the Impact of Discounts on Profitability":"""
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
    """,
    "13.Find the Average Order Value (AOV) Per Segment":"""
        SELECT segment, 
        ROUND(SUM(sale_price * quantity) / COUNT(DISTINCT order_id), 2) AS avg_order_value
        FROM df3 
        GROUP BY segment
        ORDER BY avg_order_value DESC;
    """,
    "14.Identify the Products With the Highest Order Frequency":"""
        SELECT a.product_id, b.sub_category, b.category, 
        COUNT(DISTINCT a.order_id) AS order_count
        FROM df3 a
        JOIN df2 b ON a.product_id = b.product_id
        GROUP BY a.product_id, b.sub_category, b.category
        ORDER BY order_count DESC
        LIMIT 10;
    """,
    "15.Find the Number of Orders Per Region":"""
        SELECT region, 
        COUNT(DISTINCT order_id) AS order_count
        FROM df3 
        GROUP BY region
        ORDER BY order_count DESC;
    """,
    "16.Find the Month With the Highest Sales" : """
        SELECT EXTRACT(YEAR FROM order_date) AS year, 
        EXTRACT(MONTH FROM order_date) AS month, 
        ROUND(SUM(sale_price * quantity), 2) AS total_sales
        FROM df3 
        GROUP BY year, month
        ORDER BY total_sales DESC;
    """,
    "17.Identify the Top 5 States With the Highest Revenue":"""
        SELECT state, 
        ROUND(SUM(sale_price * quantity), 2) AS total_revenue
        FROM df3 
        GROUP BY state
        ORDER BY total_revenue DESC
        LIMIT 5;
    """,
    "18.Calculate the Profit Margin Per Category":"""
        SELECT b.category, 
        ROUND(SUM(a.profit) / NULLIF(SUM(a.sale_price * a.quantity), 0) * 100, 2) AS profit_margin
        FROM df3 a
        JOIN df2 b ON a.product_id = b.product_id
        GROUP BY b.category
        ORDER BY profit_margin DESC;
    """,
    "19.Identify the Most Discounted Products":"""
        SELECT a.product_id, b.sub_category, b.category, 
        ROUND(AVG(a.discount_percent) * 100, 2) AS avg_discount_percentage
        FROM df3 a
        JOIN df2 b ON a.product_id = b.product_id
        GROUP BY a.product_id, b.sub_category, b.category
        ORDER BY avg_discount_percentage DESC;
    """,
    "20.Identify the highest revenue-generating segment":"""
        SELECT segment, 
        ROUND(SUM(sale_price * quantity), 2) AS total_revenue
        FROM df3 
        GROUP BY segment
        ORDER BY total_revenue DESC;
    """,
    "21.Query sales data by region to identify which areas are performing best": """
        SELECT region, 
        ROUND(SUM(sale_price * quantity),2) AS total_revenue,
        ROUND(SUM(profit),2) AS total_profit, 
        COUNT(DISTINCT order_id) AS order_count FROM df3
        GROUP BY region
        ORDER BY total_revenue DESC;
    """,
    "22.Compare year-over-year sales to identify growth or decline in certain months":"""
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
        ORDER BY month, year;"""
}

# Create two equal columns
col1, col2 = st.columns(2)

# Split query options into two halves
query_keys = list(query_options.keys())
first_half = query_keys[:10]  
second_half = query_keys[10:]  

# Determine which query is selected
with col1:
    selected_query1 = st.selectbox("Select an Insight (Set 1)", [""] + first_half, key="query1")

with col2:
    selected_query2 = st.selectbox("Select an Insight (Set 2)", [""] + second_half, key="query2")

def run_query(query):
    cursor.execute(query)
    data = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    return pd.DataFrame(data, columns=columns)

# Function to generate visualizations dynamically
def generate_chart(df, selected_query, col):
    if df.empty:
        col.warning("No data available for this query.")
        return

    

    # Visualization Selection
    chart_type = col.selectbox(f"Choose a Chart Type for {selected_query}:", [
        "Bar Chart", "Line Chart", "Pie Chart", "Donut Chart",
        "3D Scatter Plot", "Animated Bar Chart", "Sunburst Chart",
        "Treemap", "Heatmap", "Bubble Chart"
    ], key=f"chart_type_{selected_query}")

    fig = None

    # Standard Charts
    if chart_type == "Bar Chart":
        fig = px.bar(df, x=df.columns[0], y=df.columns[-1], text_auto=True, title=selected_query)
    elif chart_type == "Line Chart":
        fig = px.line(df, x=df.columns[0], y=df.columns[-1], markers=True, title=selected_query)
    elif chart_type == "Pie Chart":
        fig = px.pie(df, names=df.columns[0], values=df.columns[-1], title=selected_query)
    elif chart_type == "Donut Chart":
        fig = px.pie(df, names=df.columns[0], values=df.columns[-1], hole=0.4, title=selected_query)

    # Advanced Charts
    elif chart_type == "3D Scatter Plot":
        fig = px.scatter_3d(df, x=df.columns[0], y=df.columns[1], z=df.columns[-1], color=df.columns[1], title="3D Data Visualization")
    elif chart_type == "Animated Bar Chart":
        if "year" in df.columns:
            fig = px.bar(df, x="year", y=df.columns[-1], animation_frame="year", title="Animated Yearly Sales Trend")
        else:
            col.warning("Animated charts require a time-based column like 'year'.")
    elif chart_type == "Sunburst Chart":
        fig = px.sunburst(df, path=[df.columns[0], df.columns[1]], values=df.columns[-1], title="Sunburst Chart")
    elif chart_type == "Treemap":
        fig = px.treemap(df, path=[df.columns[0]], values=df.columns[-1], title="Treemap Visualization")
    elif chart_type == "Heatmap":
        fig = px.density_heatmap(df, x=df.columns[0], y=df.columns[1], z=df.columns[-1], title="Heatmap Analysis")
    elif chart_type == "Bubble Chart":
        fig = px.scatter(df, x=df.columns[0], y=df.columns[-1], size=df.columns[-1], color=df.columns[1], title="Bubble Chart Representation")

    if fig:
        col.plotly_chart(fig)



# Run the selected queries and display results
with col1:
    if selected_query1:
        st.subheader(f"Results for: {selected_query1}")
        df1 = run_query(query_options[selected_query1])
        st.dataframe(df1)
        if not df1.empty:
            generate_chart(df1, selected_query1, col1)
        
        # **Single-Line Summary Extraction**    
        summary_text1 = ""

        if not df1.empty:
            if selected_query1 == "1.Find top 10 highest revenue generating products":
                top_product = df1.iloc[0]
                summary_text1 = f"📌 **Top-selling product:** {top_product['product_id']} in {top_product['category']} category with revenue of **₹{top_product['revenue']}**"
            
            elif selected_query1 == "2.Find the top 5 cities with the highest profit margins":
                top_city = df1.iloc[0]
                summary_text1 = f"🏙️ **Top city by profit margin:** {top_city['city']} with a profit margin of **{top_city['profit_margin']}%**"
            
            elif selected_query1 == "3.Calculate the total discount given for each category":
                top_discount_category = df1.iloc[0]
                summary_text1 = f"💰 **Category with the highest discount:** {top_discount_category['category']} with a total discount of **₹{top_discount_category['total_discount']}**"

            elif selected_query1 == "4.Find the average sale price per product category":
                highest_avg_price_category = df1.iloc[0]  
                summary_text1 = f"💲 **Highest average sale price category:** {highest_avg_price_category['category']} with an average sale price of **₹{highest_avg_price_category['avg_sale_price']}**"
             
            elif selected_query1 == "5.Find the region with the highest average sale price":
                top_region = df1.iloc[0]  
                summary_text1 = f"🌍 **Region with the highest average sale price:** {top_region['region']} with an average sale price of **₹{top_region['avg_sale_price']}**"

            elif selected_query1 == "6.Find the total profit per category":
                top_profit_category = df1.iloc[0]  
                summary_text1 = f"📈 **Category with the highest total profit:** {top_profit_category['category']} with a total profit of **₹{top_profit_category['total_profit']}**"

            elif selected_query1 == "7.Identify the top 3 segments with the highest quantity of orders.":
                top_segment = df1.iloc[0]  
                summary_text1 = f"📦 **Top segment by order quantity:** {top_segment['segment']} with **{top_segment['total_quantity']}** orders."
                 
            elif selected_query1 == "8.Determine the average discount percentage given per region":
                top_discount_region = df1.iloc[0]  
                summary_text1 = f"💳 **Region with the highest average discount:** {top_discount_region['region']} with an average discount of **{top_discount_region['avg_discount_percent']}**"
                 
            elif selected_query1 == "9.Find the product category with the highest total profit":
                top_profit_category = df1.iloc[0]  
                summary_text1 = f"🏆 **Category with the highest total profit:** {top_profit_category['category']} with a total profit of **₹{top_profit_category['total_profit']}**"
                 
            elif selected_query1 == "10.Calculate the total revenue generated per year":
                latest_year = df1.iloc[-1] 
                summary_text1 = f"📅 **Total revenue in {latest_year['year']}:** ₹{latest_year['total_revenue']}"
        else:
            summary_text1 = "❌ No data available for this query."

        # Display summary for Set 1
        if summary_text1:
            st.markdown(f"**🔍 Summary:** {summary_text1}")
            

with col2:
    if selected_query2:
        st.subheader(f"Results for: {selected_query2}")
        df2 = run_query(query_options[selected_query2])
        st.dataframe(df2)
        if not df2.empty:
            generate_chart(df2, selected_query2, col2)

        # **Single-Line Summary Extraction**
        summary_text2 = ""
             
        if not df2.empty:
            if selected_query2 == "11.Identify the Regions With the Highest Repeat Orders": 
                summary_text2 = "❌ No repeat"
                 
            elif selected_query2 == "12.Determine the Impact of Discounts on Profitability":
                high_discount = df2[df2['discount_category'] == 'High Discount (>20%)']
                low_discount = df2[df2['discount_category'] == 'Low Discount (≤20%)']

                if not high_discount.empty and not low_discount.empty:
                    high_discount = high_discount.iloc[0]
                    low_discount = low_discount.iloc[0]
                
                    summary_text2 = (
                        f"📉 **High Discount (>20%)**: Profit Margin **{high_discount['profit_margin']}%** on revenue of ₹{high_discount['total_revenue']}."
                        f"📈 **Low Discount (≤20%)**: Profit Margin **{low_discount['profit_margin']}%** on revenue of ₹{low_discount['total_revenue']}**.")
                
                elif not high_discount.empty:
                    high_discount = high_discount.iloc[0]
                    summary_text2 = (
                        f"📉 **High Discount (>20%)**: Profit Margin **{high_discount['profit_margin']}%** on revenue of ₹{high_discount['total_revenue']}. "
                        f"❌ No data available for Low Discount (≤20%).")
                
                elif not low_discount.empty:
                    low_discount = low_discount.iloc[0]
                    summary_text2 = (
                        f"📈 **Low Discount (≤20%)**: Profit Margin **{low_discount['profit_margin']}%** on revenue of ₹{low_discount['total_revenue']}**. "
                        f"❌ No data available for High Discount (>20%).")

            elif selected_query2 == "13.Find the Average Order Value (AOV) Per Segment":
                top_aov_segment = df2.iloc[0] 
                summary_text2 = f"💰 **Segment with the highest Average Order Value (AOV):** {top_aov_segment['segment']} with an AOV of **₹{top_aov_segment['avg_order_value']}**"

            elif selected_query2 == "14.Identify the Products With the Highest Order Frequency":
                top_product = df2.iloc[0] 
                summary_text2 = f"📦 **Most frequently ordered product:** {top_product['product_id']} ({top_product['category']} - {top_product['sub_category']}) with **{top_product['order_count']}** orders."

            elif selected_query2 == "15.Find the Number of Orders Per Region":
                top_region = df2.iloc[0] 
                summary_text2 = f"🌍 **Region with the highest number of orders:** {top_region['region']} with **{top_region['order_count']}** orders."
                 
            elif selected_query2 == "16.Find the Month With the Highest Sales":
                top_month = df2.iloc[0]  
                summary_text2 = f"📅 **Month with the highest sales:** {top_month['month']}/{top_month['year']} with total sales of **₹{top_month['total_sales']}**."
                 
            elif selected_query2 == "17.Identify the Top 5 States With the Highest Revenue":
                top_states = df2.head(5) 
                summary_text2 = "🏆 **Top 5 states with the highest revenue:**\n" + "\n".join(
                    [f"🥇 {row['state']} - ₹{row['total_revenue']}" for _, row in top_states.iterrows()])
                 
            elif selected_query2 == "18.Calculate the Profit Margin Per Category":
                top_category = df2.iloc[0]  
                summary_text2 = f"📊 **Category with the highest profit margin:** {top_category['category']} with a profit margin of **{top_category['profit_margin']}%**."

            elif selected_query2 == "19.Identify the Top 5 Most Discounted Products":
                top_products = df2.head(5)  
                summary_text2 = "🔻 **Top 5 most discounted products:**\n" + "\n".join(
                    [f"🎯 {row['product_id']} ({row['category']} - {row['sub_category']}) - {row['avg_discount_percentage']}% discount"
                     for _, row in top_products.iterrows()])
                
            elif selected_query2 == "20.Identify the highest revenue-generating segment":
                top_segment = df2.iloc[0]  
                summary_text2 = f"💼 **Segment generating the highest revenue:** {top_segment['segment']} with total revenue of **₹{top_segment['total_revenue']}**."

            elif selected_query2 == "21.Query sales data by region to identify which areas are performing best":  
                top_region = df2.iloc[0]  
                summary_text2 = f"🌍 **Top-performing region:** {top_region['region']} with total sales of **₹{top_region['total_revenue']}**."

            elif selected_query2 == "22.Compare year-over-year sales to identify growth or decline in certain months":  
                top_month = df2.iloc[1]  
                summary_text2 = f"📊 **Year-over-year sales trend:** {top_month['month']} shows a **{top_month['year_growth']}%** change compared to last year."
        else:
            summary_text2 = "❌ No data available for this query."

        # Display summary for Set 2
        if summary_text2:
            st.markdown(f"**🔍 Summary:** {summary_text2}")
            

# Close DB connection
myconnection.close()
