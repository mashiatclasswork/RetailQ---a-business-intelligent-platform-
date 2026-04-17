import streamlit as st
from db import run_query, write_query

st.set_page_config(page_title="Reports - RetailIQ", layout="wide")

st.markdown("""
<style>
    html, body, [class*="css"] { font-family: -apple-system, BlinkMacSystemFont, sans-serif; font-size: 18px; }
    .stApp { background: linear-gradient(135deg, #dbeafe 0%, #eff6ff 100%); }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #1e3a8a 0%, #1a56db 100%); }
    [data-testid="stSidebar"] * { color: #ffffff !important; font-size: 16px !important; }
    h1 { font-size: 42px !important; font-weight: 700 !important; color: #1e3a8a !important; }
    h2, h3 { font-size: 26px !important; font-weight: 600 !important; color: #1e3a8a !important; }
    p, label, div, span { font-size: 16px !important; color: #1e3a5f !important; }
    .stButton > button {
        background-color: #1a56db !important; color: white !important;
        border: none !important; border-radius: 12px !important;
        padding: 12px 28px !important; font-size: 16px !important;
        font-weight: 600 !important; width: 100%;
    }
    div[data-testid="stDataFrame"] { border-radius: 16px; border: 1px solid #bfdbfe; background: white; }
    .block-container { padding-top: 2rem; max-width: 1300px; }
    .info-box {
        background: white; border-radius: 16px; padding: 20px 24px;
        margin: 12px 0; border-left: 5px solid #1a56db;
        font-size: 16px !important; color: #1e3a5f !important;
        line-height: 1.7; box-shadow: 0 2px 8px rgba(26,86,219,0.08);
    }
    .query-box {
        background: #1e3a8a; color: #e0f2fe;
        border-radius: 16px; padding: 20px 24px;
        font-family: 'SF Mono', 'Courier New', monospace;
        font-size: 14px !important; line-height: 1.8;
        white-space: pre-wrap; margin: 12px 0;
        border: 1px solid #1a56db;
    }
    hr { border: none; border-top: 2px solid #bfdbfe; margin: 2rem 0; }
    .stSelectbox > div { border-radius: 12px !important; border: 2px solid #bfdbfe !important; }
</style>
""", unsafe_allow_html=True)

st.title("Business Reports")
st.markdown("---")

tab1, tab2 = st.tabs(["📊  Run a Report", "➕  Add New Product"])

with tab1:
    QUERIES = {
        "Who are all our customers?": {
            "sql": """SELECT CustomerID,
       CONCAT(FirstName, ' ', LastName) AS CustomerName,
       Gender, Age,
       YEAR(RegistrationDate) AS RegistrationYear
FROM CUSTOMERS
ORDER BY RegistrationDate DESC""",
            "explanation": "Returns the full customer list sorted by most recently registered. Useful for getting a complete snapshot of all users in the system."
        },
        "Who are our High Value customers?": {
            "sql": """SELECT c.CustomerID,
       CONCAT(c.FirstName, ' ', c.LastName) AS CustomerName,
       c.Email, s.SegmentLabel, s.ClusterID
FROM CUSTOMERS c
JOIN SEGMENTATION_RESULTS s ON c.CustomerID = s.CustomerID
WHERE s.SegmentLabel = 'High Value'
ORDER BY c.CustomerID""",
            "explanation": "Uses a JOIN to filter only High Value customers. These are your most profitable customers — consider loyalty rewards and exclusive offers for this group."
        },
        "Which customers have never made a purchase?": {
            "sql": """SELECT c.CustomerID,
       CONCAT(c.FirstName, ' ', c.LastName) AS CustomerName,
       c.Age, c.Gender, c.Email, c.Phone
FROM CUSTOMERS c
LEFT JOIN TRANSACTIONS t ON c.CustomerID = t.CustomerID
WHERE t.CustomerID IS NULL""",
            "explanation": "Uses a LEFT JOIN with IS NULL to find registered customers with zero transactions. These are prime targets for first-purchase discount campaigns."
        },
        "What is the revenue by product category?": {
            "sql": """SELECT p.Category,
       COUNT(t.TransactionID) AS TotalOrders,
       ROUND(SUM(t.TotalAmount), 2) AS TotalRevenue,
       ROUND(AVG(t.TotalAmount), 2) AS AvgOrderValue
FROM TRANSACTIONS t
JOIN PRODUCTS p ON t.ProductID = p.ProductID
GROUP BY p.Category
ORDER BY TotalRevenue DESC""",
            "explanation": "Groups all transactions by product category to show total revenue, order count and average order value per category. Use this to identify your strongest and weakest performing product lines."
        },
        "What are the top 5 best selling products?": {
            "sql": """SELECT ProductName, Category, TotalSold
FROM (
    SELECT p.ProductName, p.Category,
           SUM(t.Quantity) AS TotalSold
    FROM TRANSACTIONS t
    JOIN PRODUCTS p ON t.ProductID = p.ProductID
    GROUP BY p.ProductID, p.ProductName, p.Category
) AS ProductSales
ORDER BY TotalSold DESC
LIMIT 5""",
            "explanation": "Uses a subquery to calculate total units sold per product, then returns only the top 5. Use this to ensure your best sellers are always in stock."
        },
        "Which customers spend above average?": {
            "sql": """SELECT c.CustomerID,
       CONCAT(c.FirstName, ' ', c.LastName) AS CustomerName,
       ROUND(bm.AverageSpending, 2) AS AverageSpending
FROM CUSTOMERS c
JOIN BEHAVIORAL_METRICS bm ON c.CustomerID = bm.CustomerID
WHERE bm.AverageSpending > (
    SELECT AVG(AverageSpending)
    FROM BEHAVIORAL_METRICS
    WHERE AverageSpending > 0
)
ORDER BY bm.AverageSpending DESC""",
            "explanation": "Identifies customers whose average spending exceeds the company-wide average. These customers are your best upsell and premium product targets."
        },
        "Who are our most frequent buyers?": {
            "sql": """SELECT t.CustomerID,
       CONCAT(c.FirstName, ' ', c.LastName) AS CustomerName,
       COUNT(t.TransactionID) AS TotalTransactions,
       ROUND(SUM(t.TotalAmount), 2) AS TotalSpent
FROM TRANSACTIONS t
JOIN CUSTOMERS c ON t.CustomerID = c.CustomerID
GROUP BY t.CustomerID, c.FirstName, c.LastName
HAVING COUNT(t.TransactionID) > 3
ORDER BY TotalTransactions DESC""",
            "explanation": "Finds customers who have placed more than 3 orders using GROUP BY and HAVING. These are your loyal repeat buyers — ideal candidates for subscription or membership programs."
        },
        "What is each customer's lifetime value?": {
            "sql": """WITH CustomerLTV AS (
    SELECT c.CustomerID,
           CONCAT(c.FirstName, ' ', c.LastName) AS CustomerName,
           COUNT(t.TransactionID) AS TotalOrders,
           ROUND(SUM(t.TotalAmount), 2) AS LifetimeValue,
           ROUND(AVG(t.TotalAmount), 2) AS AvgOrderValue,
           DATEDIFF(CURDATE(), MAX(t.TransactionDate)) AS DaysSinceLastOrder
    FROM CUSTOMERS c
    JOIN TRANSACTIONS t ON c.CustomerID = t.CustomerID
    GROUP BY c.CustomerID, c.FirstName, c.LastName
)
SELECT ltv.CustomerID, ltv.CustomerName,
       ltv.TotalOrders, ltv.LifetimeValue,
       ltv.AvgOrderValue, ltv.DaysSinceLastOrder,
       sr.SegmentLabel
FROM CustomerLTV ltv
JOIN SEGMENTATION_RESULTS sr ON ltv.CustomerID = sr.CustomerID
ORDER BY ltv.LifetimeValue DESC""",
            "explanation": "Uses a CTE to calculate each customer's total lifetime value, average order value, and days since their last purchase. Combine with segment data to prioritize high-LTV customers for retention efforts."
        },
        "What is the top selling product in each category?": {
            "sql": """SELECT Category, ProductName, TotalRevenue, TotalUnitsSold
FROM (
    SELECT p.Category, p.ProductName,
           ROUND(SUM(t.TotalAmount), 2) AS TotalRevenue,
           SUM(t.Quantity) AS TotalUnitsSold,
           RANK() OVER (
               PARTITION BY p.Category
               ORDER BY SUM(t.TotalAmount) DESC
           ) AS rnk
    FROM PRODUCTS p
    JOIN TRANSACTIONS t ON p.ProductID = t.ProductID
    GROUP BY p.Category, p.ProductName
) ranked
WHERE rnk = 1""",
            "explanation": "Uses the RANK() window function to rank products within each category by revenue, then returns only the number 1 ranked product per category. Use this to identify your category champions."
        },
        "Show male customers aged 30 to 50": {
            "sql": """SELECT CustomerID,
       CONCAT(FirstName, ' ', LastName) AS CustomerName,
       Age, Email, Phone
FROM CUSTOMERS
WHERE Gender = 'Male'
  AND Age BETWEEN 30 AND 50
ORDER BY Age""",
            "explanation": "A targeted demographic filter for male customers between 30 and 50. Use this list for age-targeted campaigns, promotions, or market research."
        }
    }

    selected = st.selectbox("Select a report to run", list(QUERIES.keys()))
    selected_query = QUERIES[selected]

    st.markdown(f"""
    <div class='info-box'>
    {selected_query['explanation']}
    </div>
    """, unsafe_allow_html=True)

    with st.expander("View SQL Query"):
        st.markdown(f"""
        <div class='query-box'>{selected_query['sql']}</div>
        """, unsafe_allow_html=True)

    if st.button("Run Report", type="primary"):
        with st.spinner("Running report..."):
            result = run_query(selected_query["sql"])
        st.success(f"{len(result)} rows returned")
        st.dataframe(result, use_container_width=True, hide_index=True)
        csv = result.to_csv(index=False)
        st.download_button(
            "Download Results as CSV",
            data=csv,
            file_name="report_results.csv",
            mime="text/csv"
        )

with tab2:
    st.subheader("Add New Product")
    st.markdown("Add a new product to the catalog.")

    with st.form("add_product_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            product_name = st.text_input("Product Name *")
            category = st.selectbox("Category *", ["Home", "Beauty", "Books", "Sports", "Electronics", "Clothing"])
        with col2:
            price = st.number_input("Price ($) *", min_value=0.01, value=9.99, step=0.01)

        submitted = st.form_submit_button("Add Product")
        if submitted:
            if not product_name:
                st.error("Please enter a product name.")
            elif price <= 0:
                st.error("Price must be greater than zero.")
            else:
                try:
                    write_query("""
                        INSERT INTO PRODUCTS (ProductName, Category, Price)
                        VALUES (%s, %s, %s)
                    """, (product_name, category, price))
                    run_query.clear()
                    st.success(f"Product '{product_name}' added successfully to {category} category!")
                except Exception as e:
                    st.error(f"Error adding product: {e}")