import streamlit as st
import plotly.express as px
from db import run_query

st.set_page_config(page_title="RetailIQ", layout="wide")

st.markdown("""
<style>
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
        font-size: 18px;
    }
    .stApp {
        background: linear-gradient(135deg, #dbeafe 0%, #eff6ff 100%);
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3a8a 0%, #1a56db 100%);
        padding-top: 0;
    }
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
        font-size: 16px !important;
    }
    [data-testid="stSidebarNav"] a {
        font-size: 16px !important;
        padding: 12px 16px !important;
        border-radius: 10px;
        margin: 4px 8px;
    }
    [data-testid="stSidebarNav"] a:hover {
        background-color: rgba(255,255,255,0.15) !important;
    }
    [data-testid="stSidebarNav"] a[aria-selected="true"] {
        background-color: rgba(255,255,255,0.25) !important;
        font-weight: 600 !important;
    }
    h1 {
        font-size: 42px !important;
        font-weight: 700 !important;
        color: #1e3a8a !important;
        margin-bottom: 8px;
    }
    h2, h3 {
        font-size: 26px !important;
        font-weight: 600 !important;
        color: #1e3a8a !important;
    }
    p, label, div, span {
        font-size: 16px !important;
        color: #1e3a5f !important;
    }
    [data-testid="stMetric"] {
        background: white;
        border-radius: 16px;
        padding: 24px 28px;
        border: none;
        box-shadow: 0 2px 12px rgba(26,86,219,0.1);
    }
    [data-testid="stMetricLabel"] {
        font-size: 15px !important;
        color: #6b7280 !important;
        font-weight: 500 !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 36px !important;
        font-weight: 700 !important;
        color: #1e3a8a !important;
    }
    .stButton > button {
        background-color: #1a56db !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 28px !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        width: 100%;
    }
    .stButton > button:hover {
        background-color: #1e40af !important;
    }
    div[data-testid="stDataFrame"] {
        border-radius: 16px;
        border: 1px solid #bfdbfe;
        background: white;
        overflow: hidden;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1300px;
    }
    .logo-box {
        background: #1e3a8a;
        border-radius: 16px;
        padding: 20px 16px;
        margin: 16px 8px 24px 8px;
        text-align: center;
    }
    .logo-title {
        font-size: 28px !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        letter-spacing: -0.5px;
    }
    .logo-sub {
        font-size: 13px !important;
        color: #93c5fd !important;
        margin-top: 4px;
    }
    .info-box {
        background: white;
        border-radius: 16px;
        padding: 20px 24px;
        margin: 12px 0;
        border-left: 5px solid #1a56db;
        font-size: 16px !important;
        color: #1e3a5f !important;
        line-height: 1.7;
        box-shadow: 0 2px 8px rgba(26,86,219,0.08);
    }
    hr {
        border: none;
        border-top: 2px solid #bfdbfe;
        margin: 2rem 0;
    }
    .stSelectbox > div, .stTextInput > div > div {
        border-radius: 12px !important;
        border: 2px solid #bfdbfe !important;
        font-size: 16px !important;
    }
</style>

<div class='logo-box'>
    <div class='logo-title'>RetailIQ</div>
    <div class='logo-sub'>Customer Intelligence Platform</div>
</div>
""", unsafe_allow_html=True)

st.title("Welcome to RetailIQ")
st.markdown(
    "<p style='font-size:20px;color:#3b82f6;margin-top:-12px;"
    "margin-bottom:24px;'>Your complete customer segmentation "
    "and analytics platform</p>",
    unsafe_allow_html=True
)
st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

total_customers = run_query("SELECT COUNT(*) as Total FROM CUSTOMERS")
total_revenue = run_query("SELECT ROUND(SUM(TotalAmount), 2) as Total FROM TRANSACTIONS")
total_transactions = run_query("SELECT COUNT(*) as Total FROM TRANSACTIONS")
total_products = run_query("SELECT COUNT(*) as Total FROM PRODUCTS")

with col1:
    st.metric("Total Customers", f"{total_customers['Total'][0]:,}")
with col2:
    st.metric("Total Revenue", f"${total_revenue['Total'][0]:,.2f}")
with col3:
    st.metric("Total Transactions", f"{total_transactions['Total'][0]:,}")
with col4:
    st.metric("Total Products", f"{total_products['Total'][0]:,}")

st.markdown("---")

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Customer Segments")
    segments = run_query("""
        SELECT SegmentLabel, COUNT(*) as Count
        FROM SEGMENTATION_RESULTS
        GROUP BY SegmentLabel
    """)
    fig = px.pie(
        segments, names="SegmentLabel", values="Count",
        color_discrete_map={
            "High Value": "#16a34a",
            "Medium Value": "#1a56db",
            "Low Value": "#dc2626"
        },
        hole=0.45
    )
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(
            family="-apple-system, sans-serif",
            size=15,
            color="#1e3a5f"
        ),
        margin=dict(t=20, b=30),
        legend=dict(
            font=dict(size=14),
            orientation="h",
            yanchor="bottom",
            y=-0.25
        )
    )
    fig.update_traces(
        textfont_size=15,
        hovertemplate="<b>%{label}</b><br>Customers: %{value}<br>Share: %{percent}<extra></extra>"
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("""
    <div class='info-box'>
    This chart shows how your 3,000 customers are split across three value tiers.
    <b>High Value</b> customers buy frequently and spend the most — protect and reward them.
    <b>Medium Value</b> customers have room to grow — target them with upsell offers.
    <b>Low Value</b> customers need re-engagement campaigns to bring them back.
    </div>
    """, unsafe_allow_html=True)

with col_right:
    st.subheader("Revenue by Category")
    revenue = run_query("""
        SELECT p.Category, ROUND(SUM(t.TotalAmount), 2) AS Revenue
        FROM TRANSACTIONS t
        JOIN PRODUCTS p ON t.ProductID = p.ProductID
        GROUP BY p.Category
        ORDER BY Revenue DESC
    """)
    fig2 = px.bar(
        revenue, x="Category", y="Revenue",
        color="Category",
        color_discrete_sequence=[
            "#1a56db","#16a34a","#f59e0b",
            "#dc2626","#7c3aed","#0891b2"
        ]
    )
    fig2.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(
            family="-apple-system, sans-serif",
            size=15,
            color="#1e3a5f"
        ),
        showlegend=False,
        margin=dict(t=20, b=20),
        xaxis=dict(showgrid=False, tickfont=dict(size=14)),
        yaxis=dict(showgrid=True, gridcolor="#eff6ff", tickfont=dict(size=14))
    )
    fig2.update_traces(
        hovertemplate="<b>%{x}</b><br>Revenue: $%{y:,.2f}<extra></extra>"
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown("""
    <div class='info-box'>
    This bar chart shows total revenue per product category.
    The tallest bar is your highest earning category — focus inventory and promotions here.
    Shorter bars indicate underperforming categories that may need pricing or marketing attention.
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.subheader("Recent Transactions")
recent = run_query("""
    SELECT
        t.TransactionID,
        CONCAT(c.FirstName, ' ', c.LastName) AS CustomerName,
        p.ProductName,
        p.Category,
        t.Quantity,
        ROUND(t.TotalAmount, 2) AS TotalAmount,
        DATE(t.TransactionDate) AS Date
    FROM TRANSACTIONS t
    JOIN CUSTOMERS c ON t.CustomerID = c.CustomerID
    JOIN PRODUCTS p ON t.ProductID = p.ProductID
    ORDER BY t.TransactionDate DESC
    LIMIT 10
""")
st.dataframe(recent, use_container_width=True, hide_index=True)