# Project Overview

## Objective

Prepare e-commerce sales records, load a star-style fact-and-dimension model into SQL Server, and communicate results through a dashboard report.

## Data journey

1. **Excel/source data:** the project began with sales data in Excel; the supplied analysis dataset is a 10,005-row CSV.
2. **Python:** `main.py` parses order dates, derives `TotalAmount`, builds dimensions for product, platform, date, and city/address, joins their keys into `fact_sales`, and removes rows missing required sales fields.
3. **Microsoft SQL Server:** pandas `to_sql` writes the model tables to the `ecommerce_10000` database on local SQL Server LocalDB.
4. **Dashboard:** the supplied two-page report shows sales KPIs and trends, product performance, category comparisons, and brand mix.

## Tables

- `fact_sales`
- `dim_product`
- `dim_platform`
- `dim_date`
- `dim_customer_address`

## Summary queries

The script queries the sales date range, counts distinct order IDs, and identifies the product with the highest total sales amount.

## Dashboard values

The first report page displays **$302.13M** total sales and **10.002K** orders for **January 1–December 26, 2024**. Its product KPI displays **10** with the label “Total Products Sold.” These values are transcribed from the dashboard and have not been reconciled against a live SQL Server run.

## Included files and limitations

The repository includes `main.py`, the supplied sales dataset as a gzip-compressed CSV, five SVG icons, Python dependency declarations, and the first two dashboard report pages. The source Excel workbook, editable dashboard project, and separate SQL scripts were not present in the supplied directory. The script creates/replaces tables through `to_sql` when run.
