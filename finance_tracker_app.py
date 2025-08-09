import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="Personal Finance Tracker", layout="centered")

# Initialize session state variables
if "income" not in st.session_state:
    st.session_state.income = 0.0
if "expenses" not in st.session_state:
    st.session_state.expenses = []
if "month" not in st.session_state:
    st.session_state.month = datetime.datetime.now().strftime("%Y-%m")

# Reset monthly if new month
current_month = datetime.datetime.now().strftime("%Y-%m")
if st.session_state.month != current_month:
    st.session_state.income = 0.0
    st.session_state.expenses = []
    st.session_state.month = current_month
    st.success("New month started! Income and expenses reset.")

st.title("💰 Personal Finance Tracker")

# Input monthly income
income = st.number_input("Enter your monthly income", min_value=0.0, value=st.session_state.income, step=100.0)
if st.button("Save Income"):
    st.session_state.income = income
    st.success(f"Monthly income set to ${income:,.2f}")

st.markdown("---")

# Add expense
st.subheader("Add an Expense")
expense_name = st.text_input("Expense Description")
expense_amount = st.number_input("Expense Amount", min_value=0.0, step=1.0, format="%.2f")

if st.button("Add Expense"):
    if expense_amount > 0 and expense_name.strip() != "":
        st.session_state.expenses.append({"name": expense_name.strip(), "amount": expense_amount})
        st.success(f"Added expense: {expense_name} - ${expense_amount:,.2f}")
    else:
        st.error("Please enter a valid expense name and amount.")

st.markdown("---")

# Calculate total expenses and remaining balance
total_expenses = sum(e["amount"] for e in st.session_state.expenses)
remaining = st.session_state.income - total_expenses

st.subheader("Summary")
st.write(f"**Monthly Income:** ${st.session_state.income:,.2f}")
st.write(f"**Total Expenses:** ${total_expenses:,.2f}")
st.write(f"**Remaining Balance:** ${remaining:,.2f}")

if remaining < 0:
    st.error("⚠️ You have exceeded your monthly income!")
elif remaining < 0.2 * st.session_state.income:
    st.warning("⚠️ Your remaining balance is low.")

st.markdown("---")

# Show expense list
st.subheader("Expenses")
if st.session_state.expenses:
    df = pd.DataFrame(st.session_state.expenses)
    st.dataframe(df)
else:
    st.info("No expenses added yet.")

