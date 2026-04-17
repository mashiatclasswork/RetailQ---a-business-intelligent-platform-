import streamlit as st
import plotly.express as px
from db import run_query

st.set_page_config(page_title="Segments - RetailIQ", layout="wide")

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
    .stat-card {
        background: white; border-radius: 20px; padding: 28px 24px;
        text-align: center; box-shadow: 0 4px 16px rgba(26,86,219,0.1);
        border: 1px solid #bfdbfe;
    }
    .stSelectbox > div { border-radius: 12px !important; border: 2px solid #bfdbfe !important; }
    hr { border: none; border-top: 2px solid #bfdbfe; margin: 2rem 0; }
</style>
""", unsafe_allow_html=True)

st.title("Customer Segments")
st.markdown("---")

summary = run_query("""
    SELECT s.SegmentLabel,
           COUNT(s.CustomerID) AS CustomerCount,
           ROUND(AVG(bm.AverageSpending), 2) AS AvgSpending,
           ROUND(AVG(bm.PurchaseFrequency), 2) AS AvgFrequency,
           ROUND(AVG(bm.RecencyOfPurchase), 0) AS AvgRecency
    FROM SEGMENTATION_RESULTS s
    JOIN BEHAVIORAL_METRICS bm ON s.CustomerID = bm.CustomerID
    GROUP BY s.SegmentLabel
    ORDER BY AvgSpending DESC
""")

col1, col2, col3 = st.columns(3)
colors = {"High Value": "#16a34a", "Medium Value": "#1a56db", "Low Value": "#dc2626"}

for i, row in summary.iterrows():
    col = [col1, col2, col3][i]
    color = colors.get(row["SegmentLabel"], "#1a56db")
    with col:
        st.markdown(f"""
        <div class='stat-card'>
            <div style='font-size:16px;color:#6b7280;margin-bottom:8px;font-weight:500;'>{row['SegmentLabel']}</div>
            <div style='font-size:48px;font-weight:800;color:{color};'>{row['CustomerCount']:,}</div>
            <div style='font-size:14px;color:#9ca3af;margin-bottom:16px;'>customers</div>
            <div style='text-align:left;font-size:15px;line-height:2;'>
                Avg Spending: <b>${row['AvgSpending']:,}</b><br>
                Avg Frequency: <b>{row['AvgFrequency']} purchases</b><br>
                Avg Recency: <b>{row['AvgRecency']} days ago</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    segment_filter = st.selectbox("Filter by segment", ["All", "High Value", "Medium Value", "Low Value"])
with col2:
    min_score = st.slider("Minimum RFM score", 3, 9, 3)

rfm = run_query("""
    SELECT c.CustomerID,
           CONCAT(c.FirstName, ' ', c.LastName) AS CustomerName,
           s.SegmentLabel,
           bm.RecencyOfPurchase,
           bm.PurchaseFrequency,
           ROUND(bm.AverageSpending, 2) AS AverageSpending,
           NTILE(3) OVER (ORDER BY bm.RecencyOfPurchase ASC)  AS RecencyScore,
           NTILE(3) OVER (ORDER BY bm.PurchaseFrequency DESC) AS FrequencyScore,
           NTILE(3) OVER (ORDER BY bm.AverageSpending DESC)   AS MonetaryScore,
           (NTILE(3) OVER (ORDER BY bm.RecencyOfPurchase ASC)
          + NTILE(3) OVER (ORDER BY bm.PurchaseFrequency DESC)
          + NTILE(3) OVER (ORDER BY bm.AverageSpending DESC)) AS RFM_Score
    FROM BEHAVIORAL_METRICS bm
    JOIN CUSTOMERS c ON bm.CustomerID = c.CustomerID
    JOIN SEGMENTATION_RESULTS s ON bm.CustomerID = s.CustomerID
    WHERE bm.PurchaseFrequency > 0
    ORDER BY RFM_Score DESC
""")

filtered = rfm[rfm["RFM_Score"] >= min_score]
if segment_filter != "All":
    filtered = filtered[filtered["SegmentLabel"] == segment_filter]

st.markdown(f"### {len(filtered)} customers match your filters")
st.dataframe(filtered, use_container_width=True, hide_index=True)

csv = filtered.to_csv(index=False)
st.download_button("Download as CSV", data=csv, file_name="rfm_segments.csv", mime="text/csv")

st.markdown("""
<div class='info-box'>
<b>RFM Score</b> ranks every customer on three dimensions:<br>
<b>Recency</b> — how recently they purchased (higher = more recent = better)<br>
<b>Frequency</b> — how often they purchase (higher = more frequent = better)<br>
<b>Monetary</b> — how much they spend (higher = more spending = better)<br><br>
A score of <b>9</b> is your most valuable customer. A score of <b>3</b> needs immediate re-engagement.
Use this list to build targeted marketing campaigns for each tier.
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.subheader("Frequency vs Average Spending by Segment")
fig = px.scatter(
    rfm, x="PurchaseFrequency", y="AverageSpending",
    color="SegmentLabel", hover_name="CustomerName",
    hover_data=["RFM_Score"],
    color_discrete_map={
        "High Value": "#16a34a",
        "Medium Value": "#1a56db",
        "Low Value": "#dc2626"
    },
    size_max=10
)
fig.update_layout(
    plot_bgcolor="white", paper_bgcolor="white",
    font=dict(size=15, color="#1e3a5f"),
    margin=dict(t=20, b=20),
    xaxis=dict(showgrid=True, gridcolor="#eff6ff", tickfont=dict(size=14)),
    yaxis=dict(showgrid=True, gridcolor="#eff6ff", tickfont=dict(size=14)),
    legend=dict(font=dict(size=14))
)
st.plotly_chart(fig, use_container_width=True)
st.markdown("""
<div class='info-box'>
Each dot represents one customer. Customers in the <b>top-right</b> corner buy often and spend a lot
— these are your most valuable customers, ideal for VIP or loyalty programs.
Customers in the <b>bottom-left</b> corner are disengaged — target them with win-back campaigns.
Hover over any dot to see the customer name and RFM score.
</div>
""", unsafe_allow_html=True)