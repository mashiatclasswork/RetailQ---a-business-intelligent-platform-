# RetailIQ — Customer Intelligence Platform

A full-stack business intelligence dashboard built with Python and Streamlit, connected to a MySQL relational database. Designed and implemented as part of a Database Management Systems course project at the University of Houston.

---

## Project Overview

RetailIQ is a database-driven customer segmentation management system that allows businesses to store, manage, analyze, and visualize customer data in real time. The system demonstrates core database concepts including relational schema design, normalization, complex SQL queries, stored procedures, triggers, views, and indexing — all surfaced through an interactive web dashboard.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Database | MySQL |
| Backend | Python |
| Frontend | Streamlit |
| Charts | Plotly |
| Data Processing | Pandas |
| Version Control | Git and GitHub |

---

## Database Schema

The system uses a normalized relational database called `dbmt_project` with the following tables:

- **CUSTOMERS** — stores customer demographics and contact information
- **PRODUCTS** — stores product catalog with categories and pricing
- **TRANSACTIONS** — records every purchase linking customers to products
- **BEHAVIORAL_METRICS** — summarizes each customer's buying behavior
- **SEGMENTATION_RESULTS** — stores clustering results labeling customers as High Value, Medium Value, or Low Value

---

## SQL Features Demonstrated

The project demonstrates 25 SQL queries across three complexity levels:

**Basic Queries**
- Full customer list with formatted names
- Transaction details with JOIN across three tables
- Filtered segment queries
- Date range filtering
- Multi-condition WHERE filters

**Intermediate Queries**
- GROUP BY with aggregate functions
- HAVING clause filtering
- Subqueries in WHERE and HAVING
- Top N queries using LIMIT

**Advanced Queries**
- Window functions: NTILE, RANK, SUM OVER, ROW_NUMBER
- Common Table Expressions (CTEs)
- RFM scoring model
- Customer Lifetime Value calculation
- Trigger for data integrity
- Stored procedure for dynamic segment lookup
- Index on SegmentLabel for query optimization
- VIEW combining multiple tables for simplified reporting

---

## Dashboard Pages

### Home
- Key metrics: total customers, total revenue, total transactions, total products
- Customer segment distribution donut chart
- Revenue by category bar chart
- Recent transactions table

### Customers
- Search customers by name
- Filter by segment, gender, and age range
- View full customer profile with purchase history
- Add new customers directly to the database

### Sales Analytics
- Filter by date range and product category
- Revenue by category bar chart
- Monthly revenue trend line chart
- Top 5 best selling products
- Downloadable CSV reports

### Customer Segments
- Segment summary cards showing High, Medium, and Low Value stats
- RFM scoring table with filters
- Frequency vs Spending scatter plot colored by segment
- Downloadable filtered customer lists

### Business Reports
- 10 pre-built business questions powered by SQL queries
- Plain English descriptions of each report
- View the underlying SQL query for each report
- Run any report and download results as CSV
- Add new products to the catalog

---

## How to Run Locally

### Prerequisites
- Python 3.8 or higher
- MySQL with the `dbmt_project` database loaded
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/mashiatclasswork/RetailQ---a-business-intelligent-platform-.git
cd RetailQ---a-business-intelligent-platform-
```

2. Install dependencies:
```bash
pip install streamlit mysql-connector-python pandas plotly
```

3. Set up your database credentials. Create a file at `.streamlit/secrets.toml`:
```toml
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "your_mysql_password"
DB_NAME = "dbmt_project"
DB_PORT = "3306"
```

4. Run the app:
```bash
streamlit run app.py
```

5. Open your browser at `http://localhost:8501`

---

## Project Structure
