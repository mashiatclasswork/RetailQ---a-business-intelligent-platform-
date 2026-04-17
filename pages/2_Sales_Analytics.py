import streamlit as st
import plotly.express as px
from db import run_query

st.set_page_config(page_title="Sales - RetailIQ", layout="wide")

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
    .stSelectbox > div, .stTextInput > div > div { border-radius: 12px !important; border: 2px solid #bfdbfe !important; }
    hr { border: none; border-top: 2px solid #bfdbfe; margin: 2rem 0; }
</style>
""", unsafe_allow_html=True)

st.title("Sales Analytics")
st.markdown("---")

col1, col2, col3 = st.columns(3)
with col1:
    start_date = st.date_input("Start date", value=None)
with col2:
    end_date = st.date_input("End date", value=None)
with col3:
    category_filter = st.selectbox(
        "Filter by category",
        ["All", "Home", "Beauty", "Books", "Sports", "Electronics", "Clothing"]
    )

date_filter = ""
if start_date and end_date:
    date_filter = f"AND t.TransactionDate BETWEEN '{start_date}' AND '{end_date}'"

cat_filter = ""
if category_filter != "All":
    cat_filter = f"AND p.Category = '{category_filter}'"

st.markdown("---")

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Revenue by Category")
    revenue_cat = run_query(f"""
        SELECT p.Category,
               COUNT(t.TransactionID) AS TotalOrders,
               ROUND(SUM(t.TotalAmount), 2) AS TotalRevenue
        FROM TRANSACTIONS t
        JOIN PRODUCTS p ON t.ProductID = p.ProductID
        WHERE 1=1 {date_filter}
        GROUP BY p.Category
        ORDER BY TotalRevenue DESC
    """)
    fig = px.bar(
        revenue_cat, x="Category", y="TotalRevenue", color="Category",
        color_discrete_sequence=["#1a56db","#16a34a","#f59e0b","#dc2626","#7c3aed","#0891b2"]
    )
    fig.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(size=15, color="#1e3a5f"),
        showlegend=False, margin=dict(t=20, b=20),
        xaxis=dict(showgrid=False, tickfont=dict(size=14)),
        yaxis=dict(showgrid=True, gridcolor="#eff6ff", tickfont=dict(size=14))
    )
    fig.update_traces(hovertemplate="<b>%{x}</b><br>Revenue: $%{y:,.2f}<extra></extra>")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("""
    <div class='info-box'>
    Total revenue broken down by product category.
    Use the date filter to compare performance across different time periods.
    The highest bar is your strongest category — consider expanding inventory there.
    </div>
    """, unsafe_allow_html=True)

with col_right:
    st.subheader("Monthly Revenue Trend")
    monthly = run_query(f"""
        SELECT DATE_FORMAT(TransactionDate, '%Y-%m') AS Month,
               ROUND(SUM(TotalAmount), 2) AS TotalRevenue
        FROM TRANSACTIONS t
        JOIN PRODUCTS p ON t.ProductID = p.ProductID
        WHERE 1=1 {date_filter} {cat_filter}
        GROUP BY Month
        ORDER BY Month
    """)
    fig2 = px.line(
        monthly, x="Month", y="TotalRevenue",
        markers=True, color_discrete_sequence=["#1a56db"]
    )
    fig2.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(size=15, color="#1e3a5f"),
        margin=dict(t=20, b=20),
        xaxis=dict(showgrid=False, tickfont=dict(size=13)),
        yaxis=dict(showgrid=True, gridcolor="#eff6ff", tickfont=dict(size=14))
    )
    fig2.update_traces(hovertemplate="<b>%{x}</b><br>Revenue: $%{y:,.2f}<extra></extra>")
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown("""
    <div class='info-box'>
    Monthly revenue trend over time.
    A rising line means business is growing. A sudden drop may signal a seasonal dip
    or an issue worth investigating. Use the category filter to isolate specific product lines.
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
col_left2, col_right2 = st.columns(2)

with col_left2:
    st.subheader("Top 5 Best Selling Products")
    top_products = run_query(f"""
        SELECT ProductName, Category, TotalSold
        FROM (
            SELECT p.ProductName, p.Category, SUM(t.Quantity) AS TotalSold
            FROM TRANSACTIONS t
            JOIN PRODUCTS p ON t.ProductID = p.ProductID
            WHERE 1=1 {cat_filter}
            GROUP BY p.ProductID, p.ProductName, p.Category
        ) AS ProductSales
        ORDER BY TotalSold DESC LIMIT 5
    """)
    fig3 = px.bar(
        top_products, x="TotalSold", y="ProductName",
        orientation="h", color="Category",
        color_discrete_sequence=["#1a56db","#16a34a","#f59e0b","#dc2626","#7c3aed"]
    )
    fig3.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(size=15, color="#1e3a5f"),
        margin=dict(t=20, b=20),
        yaxis=dict(autorange="reversed", tickfont=dict(size=13)),
        xaxis=dict(showgrid=True, gridcolor="#eff6ff")
    )
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown("""
    <div class='info-box'>
    Your top 5 products by units sold. Keep these well stocked at all times.
    These products are driving the most transaction volume across your customer base.
    </div>
    """, unsafe_allow_html=True)

with col_right2:
    st.subheader("Category Summary")
    st.dataframe(revenue_cat, use_container_width=True, hide_index=True)
    csv = revenue_cat.to_csv(index=False)
    st.download_button("Download Summary as CSV", data=csv, file_name="sales_summary.csv", mime="text/csv")