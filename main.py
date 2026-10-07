import pandas as pd
from sqlalchemy import create_engine

# Load data
data = pd.read_csv('ecommerce_10000.csv.gz', compression='gzip')

# Validate Order Date Column Type
data["OrderDate"] = pd.to_datetime(data["OrderDate"])

# Get Sales Facts
fact_sales = data[["OrderID", "Product", "City", "Price", "Platform", "OrderDate", "Quantity", "Reviews", "Rating"]].copy()

# Calculate Total Amount
fact_sales["TotalAmount"] = fact_sales["Quantity"] * fact_sales["Price"]

# -------------------------
# Dimensions
# -------------------------

dim_product = data[["Product", "Category", "Brand"]].drop_duplicates().reset_index(drop=True)
dim_product["ProductID"] = dim_product.index + 1

dim_platform = data[["Platform"]].drop_duplicates().reset_index(drop=True)
dim_platform["PlatformID"] = dim_platform.index + 1

dim_customer_address = data[["City"]].drop_duplicates().reset_index(drop=True)
dim_customer_address["AddressID"] = dim_customer_address.index + 1

dim_date = data[["OrderDate"]].drop_duplicates().reset_index(drop=True)
dim_date["DateID"] = dim_date.index + 1
dim_date["Day"] = dim_date["OrderDate"].dt.day
dim_date["Month"] = dim_date["OrderDate"].dt.month
dim_date["Year"] = dim_date["OrderDate"].dt.year

# -------------------------
# Merge Fact Table
# -------------------------

fact_sales = fact_sales.merge(dim_product[["Product", "ProductID"]], on="Product", how="left")
fact_sales = fact_sales.merge(dim_platform[["Platform", "PlatformID"]], on="Platform", how="left")
fact_sales = fact_sales.merge(dim_date[["OrderDate", "DateID"]], on="OrderDate", how="left")
fact_sales = fact_sales.merge(dim_customer_address[["City", "AddressID"]], on="City", how="left")

fact_sales = fact_sales[
    ["OrderID", "ProductID", "DateID", "PlatformID", "AddressID", "Price", "Quantity", "TotalAmount", "Rating", "Reviews"]
].dropna(subset=["TotalAmount", "OrderID", "Price"])

# MSSS Connection
SERVER_NAME = r'(localdb)\MSSQLLocalDB'
DATABASE_NAME = 'ecommerce_10000'

engine = create_engine(f"mssql+pyodbc://@{SERVER_NAME}/{DATABASE_NAME}?driver=ODBC+Driver+17+for+SQL+Server")

dim_product.to_sql("dim_product", engine, index=False, if_exists="replace")
dim_platform.to_sql("dim_platform", engine, index=False, if_exists="replace")
dim_date.to_sql("dim_date", engine, index=False, if_exists="replace")
dim_customer_address.to_sql("dim_customer_address", engine, index=False, if_exists="replace")
fact_sales.to_sql("fact_sales", engine, index=False, if_exists="replace")

# -------------------------
# Queries
# -------------------------

# most sale product
most_sale_product_query = """
SELECT TOP 1
    dp.Product, SUM(fs.TotalAmount) AS TotalSalesAmount
FROM fact_sales fs
LEFT JOIN dim_product dp ON fs.ProductID = dp.ProductID
GROUP BY dp.Product
ORDER BY TotalSalesAmount DESC
"""

most_sale_product_result = pd.read_sql(most_sale_product_query, engine)

# Sales Date Range
sales_date_range_query = """
SELECT MIN(dd.OrderDate) AS StartDate,
       MAX(dd.OrderDate) AS EndDate
FROM fact_sales fs
LEFT JOIN dim_date dd ON fs.DateID = dd.DateID;
"""

sales_date_range_result = pd.read_sql(sales_date_range_query, engine)

sales_start_date = sales_date_range_result["StartDate"].iloc[0]
sales_end_date = sales_date_range_result["EndDate"].iloc[0]

# Total Orders Count
total_orders_query = """
SELECT COUNT(DISTINCT OrderID)
FROM fact_sales
"""

total_orders_count = pd.read_sql(total_orders_query, engine).iloc[0,0]

# -------------------------
# Print Report
# -------------------------

print(f"Sales started from {sales_start_date} to {sales_end_date}")
print(f"Total orders count: {total_orders_count}")
print(f"Most sale product: \"{most_sale_product_result.iloc[0,0]}\" with total sales amount: {most_sale_product_result.iloc[0,1]}")
