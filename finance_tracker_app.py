import streamlit as st
import pandas as pd
import datetime
import altair as alt
from streamlit.components.v1 import html

# --- Page config ---
st.set_page_config(page_title="💰 Personal Finance Tracker", layout="centered")

# --- CSS styles ---
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #f7fbff 0%, #ffffff 100%);
        color: #0f172a;
    }
    .card {
        background: linear-gradient(180deg, rgba(255,255,255,0.9), rgba(250,250,255,0.9));
        border-radius: 18px;
        padding: 14px;
        box-shadow: 0 6px 20px rgba(18,38,63,0.06);
        margin-bottom: 12px;
    }
    .header {
        border-radius: 18px;
        padding: 10px;
        margin-bottom: 16px;
    }
    .small {
        font-size:12px;
        color:#5b6b79;
    }
    .big-amount {
        font-weight:700;
        font-size:22px;
        color:#05204A;
    }
    .muted {
        color:#6b7280;
    }
    .btn {
        border-radius: 10px;
        padding: 8px 12px;
    }
    .stDataFrame table {width:100%;}
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Persistence: CSV file in app root ---
CSV_PATH = "expenses_data.csv"

def load_data():
    try:
        df = pd.read_csv(CSV_PATH)
        df['Amount'] = df['Amount'].astype(float)
    except FileNotFoundError:
        df = pd.DataFrame(columns=['Month','Date','Description','Amount'])
    return df

def save_data(df):
    df.to_csv(CSV_PATH, index=False)

# --- Session state initialization ---
if "month" not in st.session_state:
    st.session_state.month = datetime.datetime.now().strftime("%Y-%m")
if "income" not in st.session_state:
    st.session_state.income = 0.0
if "last_action" not in st.session_state:
    st.session_state.last_action = None

# Load data once
df_all = load_data()

# Auto-reset monthly income when month changes (keeps history)
current_month = datetime.datetime.now().strftime("%Y-%m")
if st.session_state.month != current_month:
    st.session_state.income = 0.0
    st.session_state.month = current_month
    st.success("New month detected — income reset for the month.")

# --- Top controls: set monthly income & quick actions ---
with st.container():
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Set Monthly Income")
        income_input = st.number_input("Enter your monthly income", min_value=0.0, step=50.0, value=float(st.session_state.income))
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.write(" ")
        if st.button("💾 Save Income", key="save_income", help="Save monthly income"):
            st.session_state.income = float(income_input)
            st.success(f"Monthly income saved: ${st.session_state.income:,.2f}")
        if st.button("♻️ Reset Month (manual)", key="reset_month", help="Clear income & current month's expenses"):
            # remove current month records if user chooses to reset
            df_all = df_all[df_all['Month'] != current_month]
            save_data(df_all)
            st.session_state.income = 0.0
            st.success("Monthly data reset (expenses for current month cleared).")
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# --- Expense entry card ---
with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Add Expense")
    c1, c2, c3 = st.columns([3,1,1])
    with c1:
        desc = st.text_input("What did you spend on?", placeholder="Groceries, Transport, Coffee...")
    with c2:
        amt = st.number_input("Amount", min_value=0.0, step=1.0, format="%f")
    with c3:
        quick = st.selectbox("Quick add", ["—", "5", "10", "20", "50", "100"])
    # Quick add fills amount if chosen and amt is zero
    if quick != "—" and amt == 0.0:
        try:
            amt = float(quick)
        except:
            pass

    add_col1, add_col2 = st.columns([1,1])
    with add_col1:
        if st.button("➕ Add Expense", use_container_width=True):
            if st.session_state.income <= 0:
                st.error("⚠️ Please set your monthly income first.")
            elif amt <= 0:
                st.error("⚠️ Enter an expense amount.")
            else:
                new = {
                    "Month": current_month,
                    "Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Description": desc if desc else "No description",
                    "Amount": float(amt)
                }
                df_all = df_all.append(new, ignore_index=True)
                save_data(df_all)
                st.session_state.last_action = ("add", new)
                st.success(f"Added: {new['Description']} — ${new['Amount']:,.2f}")
    with add_col2:
        if st.button("↩️ Undo last", use_container_width=True):
            if st.session_state.last_action and st.session_state.last_action[0] == "add":
                last = st.session_state.last_action[1]
                mask = ~((df_all['Date'] == last['Date']) & (df_all['Amount'] == last['Amount']) & (df_all['Description'] == last['Description']))
                df_all = df_all[mask]
                save_data(df_all)
                st.session_state.last_action = ("undo", last)
                st.info("Last expense undone.")
            else:
                st.warning("No recent add to undo.")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# --- Summary cards ---
df_current = df_all[df_all['Month'] == current_month]
total_spent = df_current['Amount'].sum() if not df_current.empty else 0.0
remaining = float(st.session_state.income) - float(total_spent)

st.markdown(
    f"""
    <div class="card" style="display:flex; justify-content:space-between; align-items:center">
      <div>
        <div class="small">Monthly Income</div>
        <div class="big-amount">${st.session_state.income:,.2f}</div>
      </div>
      <div>
        <div class="small">Total Spent</div>
        <div class="big-amount">${total_spent:,.2f}</div>
      </div>
      <div>
        <div class="small">Remaining</div>
        <div class="big-amount">${remaining:,.2f}</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)

# --- Chart: spending trend this month ---
if not df_current.empty:
    st.subheader("Spending Trend This Month")
    df_current['DateOnly'] = pd.to_datetime(df_current['Date']).dt.date
    agg = df_current.groupby('DateOnly', as_index=False)['Amount'].sum()
    chart = alt.Chart(agg).mark_line(point=True).encode(
        x=alt.X('DateOnly:T', title='Date'),
        y=alt.Y('Amount:Q', title='Amount Spent'),
        tooltip=['DateOnly', 'Amount']
    ).properties(width='container', height=220)
    st.altair_chart(chart, use_container_width=True)

# --- Expense History with filter & export ---
st.subheader("Expense History")
with st.expander("Filter & Export"):
    colf1, colf2, colf3 = st.columns([2,2,1])
    with colf1:
        months = sorted(df_all['Month'].unique().tolist() + [current_month])
        sel_month = st.selectbox("Month", options=months, index=months.index(current_month))
    with colf2:
        text_filter = st.text_input("Search Description", "")
    with colf3:
        if st.button("Export CSV"):
            buffer = pd.compat.StringIO()
            df_all.to_csv(buffer, index=False)
            st.download_button("Download expenses.csv", data=buffer.getvalue(), file_name="expenses.csv", mime="text/csv")

    df_filtered = df_all.copy()
    if sel_month:
        df_filtered = df_filtered[df_filtered['Month'] == sel_month]
    if text_filter:
        df_filtered = df_filtered[df_filtered['Description'].str.contains(text_filter, case=False, na=False)]
    st.write(f"Showing {len(df_filtered)} records")
    st.dataframe(df_filtered.reset_index(drop=True))

else:
    st.info("No expenses recorded yet. Add your first expense above!")

# --- Footer Tips ---
st.markdown("---")
st.markdown(
    """
    <div class="card">
    <div class="small">Tips: Use the Quick Add dropdown for speedy logging. 
    Add a Google Calendar daily reminder to open this app and add expenses. 
    For permanent cloud storage consider Google Sheets integration.</div>
    </div>
    """,
    unsafe_allow_html=True,
)
