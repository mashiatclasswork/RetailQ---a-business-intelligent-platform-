import streamlit as st
from datetime import date
from db import run_query, write_query

st.set_page_config(page_title="Customers - RetailIQ", layout="wide")

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
    .profile-card {
        background: white; border-radius: 20px;
        padding: 28px 32px; margin-bottom: 20px;
        box-shadow: 0 4px 16px rgba(26,86,219,0.12);
        border: 1px solid #bfdbfe;
    }
    .profile-name { font-size: 28px !important; font-weight: 700 !important; color: #1e3a8a !important; }
    .profile-detail { font-size: 16px !important; color: #6b7280 !important; margin-top: 6px; }
    .badge-high { background:#dcfce7; color:#15803d; padding:5px 14px; border-radius:20px; font-size:14px !important; font-weight:600; }
    .badge-med { background:#dbeafe; color:#1d4ed8; padding:5px 14px; border-radius:20px; font-size:14px !important; font-weight:600; }
    .badge-low { background:#fee2e2; color:#b91c1c; padding:5px 14px; border-radius:20px; font-size:14px !important; font-weight:600; }
    .stSelectbox > div, .stTextInput > div > div { border-radius: 12px !important; border: 2px solid #bfdbfe !important; font-size: 16px !important; }
    hr { border: none; border-top: 2px solid #bfdbfe; margin: 2rem 0; }
</style>
""", unsafe_allow_html=True)

st.title("Customers")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["🔍  Search & Filter", "👤  Customer Profile", "➕  Add New Customer"])

with tab1:
    st.subheader("Search and Filter Customers")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        search = st.text_input("Search by name", placeholder="e.g. John Smith")
    with col2:
        segment = st.selectbox("Segment", ["All", "High Value", "Medium Value", "Low Value"])
    with col3:
        gender = st.selectbox("Gender", ["All", "Male", "Female"])
    with col4:
        age_range = st.slider("Age range", 18, 80, (18, 80))

    query = """
        SELECT c.CustomerID,
               CONCAT(c.FirstName, ' ', c.LastName) AS CustomerName,
               c.Age, c.Gender, c.Email, c.Phone,
               sr.SegmentLabel,
               bm.PurchaseFrequency,
               ROUND(bm.AverageSpending, 2) AS AverageSpending,
               bm.RecencyOfPurchase
        FROM CUSTOMERS c
        LEFT JOIN SEGMENTATION_RESULTS sr ON c.CustomerID = sr.CustomerID
        LEFT JOIN BEHAVIORAL_METRICS bm ON c.CustomerID = bm.CustomerID
        WHERE c.Age BETWEEN {age_min} AND {age_max}
    """.format(age_min=age_range[0], age_max=age_range[1])

    if segment != "All":
        query += f" AND sr.SegmentLabel = '{segment}'"
    if gender != "All":
        query += f" AND c.Gender = '{gender}'"
    if search:
        query += f" AND CONCAT(c.FirstName, ' ', c.LastName) LIKE '%{search}%'"
    query += " ORDER BY bm.AverageSpending DESC LIMIT 200"

    df = run_query(query)
    st.markdown(f"### {len(df)} customers found")
    st.dataframe(df, use_container_width=True, hide_index=True)
    csv = df.to_csv(index=False)
    st.download_button("Download as CSV", data=csv, file_name="customers.csv", mime="text/csv")

    st.markdown("""
    <div class='info-box'>
    Use the filters above to narrow down your customer list.
    <b>High Value</b> customers have the highest average spending — ideal for loyalty programs.
    <b>Medium Value</b> customers are growth opportunities — target with upsell campaigns.
    <b>Low Value</b> customers need re-engagement — consider discount or win-back offers.
    Download the filtered list to use in your marketing tools.
    </div>
    """, unsafe_allow_html=True)

with tab2:
    st.subheader("Customer Profile Lookup")
    st.markdown("Enter a Customer ID to see their full profile, segment and purchase history.")
    col1, col2 = st.columns([1, 3])
    with col1:
        customer_id = st.number_input("Customer ID", min_value=1, step=1, value=1)
        view_btn = st.button("View Profile")

    if view_btn:
        customer = run_query(f"""
            SELECT c.CustomerID,
                   CONCAT(c.FirstName, ' ', c.LastName) AS CustomerName,
                   c.Age, c.Gender, c.Email, c.Phone,
                   DATE(c.RegistrationDate) AS RegistrationDate,
                   sr.SegmentLabel,
                   bm.PurchaseFrequency,
                   ROUND(bm.AverageSpending, 2) AS AverageSpending,
                   bm.RecencyOfPurchase
            FROM CUSTOMERS c
            LEFT JOIN SEGMENTATION_RESULTS sr ON c.CustomerID = sr.CustomerID
            LEFT JOIN BEHAVIORAL_METRICS bm ON c.CustomerID = bm.CustomerID
            WHERE c.CustomerID = {customer_id}
        """)

        if len(customer) == 0:
            st.error("No customer found with this ID.")
        else:
            row = customer.iloc[0]
            badge = "badge-high" if row["SegmentLabel"] == "High Value" else ("badge-med" if row["SegmentLabel"] == "Medium Value" else "badge-low")
            st.markdown(f"""
            <div class='profile-card'>
                <div class='profile-name'>{row['CustomerName']}</div>
                <div class='profile-detail'>
                    ID: {row['CustomerID']} &nbsp;|&nbsp;
                    {row['Gender']} &nbsp;|&nbsp;
                    Age {row['Age']} &nbsp;|&nbsp;
                    Registered: {row['RegistrationDate']}
                </div>
                <div style='margin-top:12px;'>
                    <span class='{badge}'>{row['SegmentLabel']}</span>
                </div>
                <div style='margin-top:24px;display:grid;grid-template-columns:repeat(3,1fr);gap:16px;'>
                    <div style='background:#eff6ff;border-radius:12px;padding:16px;text-align:center;'>
                        <div style='font-size:13px;color:#6b7280;'>Purchase Frequency</div>
                        <div style='font-size:32px;font-weight:700;color:#1e3a8a;'>{row['PurchaseFrequency']}</div>
                    </div>
                    <div style='background:#eff6ff;border-radius:12px;padding:16px;text-align:center;'>
                        <div style='font-size:13px;color:#6b7280;'>Avg Spending</div>
                        <div style='font-size:32px;font-weight:700;color:#1e3a8a;'>${row['AverageSpending']:,}</div>
                    </div>
                    <div style='background:#eff6ff;border-radius:12px;padding:16px;text-align:center;'>
                        <div style='font-size:13px;color:#6b7280;'>Days Since Last Purchase</div>
                        <div style='font-size:32px;font-weight:700;color:#1e3a8a;'>{row['RecencyOfPurchase']}</div>
                    </div>
                </div>
                <div style='margin-top:16px;font-size:15px;color:#6b7280;'>
                    📧 {row['Email']} &nbsp;&nbsp; 📞 {row['Phone']}
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.subheader("Purchase History")
            history = run_query(f"""
                SELECT t.TransactionID, p.ProductName, p.Category,
                       t.Quantity, ROUND(t.TotalAmount, 2) AS TotalAmount,
                       DATE(t.TransactionDate) AS Date
                FROM TRANSACTIONS t
                JOIN PRODUCTS p ON t.ProductID = p.ProductID
                WHERE t.CustomerID = {customer_id}
                ORDER BY t.TransactionDate DESC
            """)
            if len(history) == 0:
                st.warning("This customer has no transactions yet.")
            else:
                st.success(f"{len(history)} transactions found")
                st.dataframe(history, use_container_width=True, hide_index=True)

with tab3:
    st.subheader("Add New Customer")
    st.markdown("Register a new customer directly into the database.")

    with st.form("add_customer_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name *")
            age = st.number_input("Age *", min_value=18, max_value=100, value=25)
            email = st.text_input("Email *")
        with col2:
            last_name = st.text_input("Last Name *")
            gender = st.selectbox("Gender *", ["Male", "Female"])
            phone = st.text_input("Phone")

        submitted = st.form_submit_button("Add Customer")
        if submitted:
            if not first_name or not last_name or not email:
                st.error("Please fill in all required fields marked with *")
            else:
                try:
                    write_query("""
                        INSERT INTO CUSTOMERS
                            (FirstName, LastName, Age, Gender, Email, Phone, RegistrationDate)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (first_name, last_name, age, gender, email, phone, date.today()))
                    run_query.clear()
                    st.success(f"Customer {first_name} {last_name} added successfully!")
                except Exception as e:
                    st.error(f"Error adding customer: {e}")