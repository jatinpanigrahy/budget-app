import streamlit as st
import pandas as pd


# ==========================================
# CORE LOGIC
# ==========================================
class Category:
    def __init__(self, name):
        self.name = name
        self.ledger = []

    def deposit(self, amount, description=""):
        self.ledger.append({"amount": float(amount), "description": description})

    def withdraw(self, amount, description=""):
        if self.check_funds(amount):
            self.ledger.append({"amount": -float(amount), "description": description})
            return True
        return False

    def get_balance(self):
        return sum(entry["amount"] for entry in self.ledger)

    def check_funds(self, amount):
        return float(amount) <= self.get_balance()


# ==========================================
# MEMORY & SETUP
# ==========================================
st.set_page_config(page_title="Budget App", layout="wide")

# Set active user
if "current_user" not in st.session_state:
    st.session_state.current_user = "Default Account"

# Setup the primary database structure: { "Username": { "CategoryName": CategoryObject } }
if "database" not in st.session_state:
    st.session_state.database = {}


# Initialize default data for any new user
def initialize_user(username):
    if username not in st.session_state.database:
        st.session_state.database[username] = {
            "Food": Category("Food"),
            "Housing": Category("Housing"),
            "Transport": Category("Transport"),
        }


initialize_user(st.session_state.current_user)

# Shortcut variable for the active user's data
active_data = st.session_state.database[st.session_state.current_user]

# ==========================================
# UI: HEADER & SETTINGS
# ==========================================
st.title("Budget App")

with st.expander("How to use this app"):
    st.markdown("""
    1. **Add Categories:** Create custom categories for your expenses.
    2. **Log Transactions:** Deposit funds or record withdrawals.
    3. **Track Balances:** The dashboard updates automatically to show your remaining funds and spending habits.
    *Note: Changing the account name below acts like switching user profiles.*
    """)

col_user, _ = st.columns([1, 3])
with col_user:
    new_user = st.text_input("Active Account", value=st.session_state.current_user)
    if new_user != st.session_state.current_user and new_user.strip() != "":
        st.session_state.current_user = new_user.strip()
        initialize_user(st.session_state.current_user)
        st.rerun()

st.divider()

# ==========================================
# UI: MAIN DASHBOARD
# ==========================================
col_transact, col_data = st.columns([1, 2])

with col_transact:
    st.subheader("Manage Funds")

    # NEW UI: Dedicated Category Creation
    new_cat = st.text_input("Create New Category", placeholder="e.g. Subscriptions")
    if st.button("Add Category"):
        clean_name = new_cat.strip()
        if clean_name and clean_name not in active_data:
            active_data[clean_name] = Category(clean_name)
            st.success(f"Added {clean_name}")
            st.rerun()
        elif clean_name in active_data:
            st.error("Category already exists.")

    st.markdown("---")

    # Transaction Execution
    cat_options = list(active_data.keys())
    if not cat_options:
        st.warning("Please add a category first.")
    else:
        selected_cat = st.selectbox("Select Category", cat_options)
        action = st.radio("Action", ["Deposit", "Withdraw"], horizontal=True)
        amount = st.number_input("Amount ($)", min_value=0.01, step=10.0, format="%.2f")
        desc = st.text_input("Description (Optional)")

        if st.button("Submit"):
            cat_obj = active_data[selected_cat]
            if action == "Deposit":
                cat_obj.deposit(amount, desc)
                st.success("Deposit logged.")
                st.rerun()
            elif action == "Withdraw":
                if cat_obj.withdraw(amount, desc):
                    st.success("Withdrawal logged.")
                    st.rerun()
                else:
                    st.error("Insufficient funds in this category.")

with col_data:
    st.subheader("Overview")

    # Force table to render even if data is zero
    balance_data = []
    withdrawal_data = []

    for name, cat_obj in active_data.items():
        bal = cat_obj.get_balance()
        balance_data.append({"Category": name, "Balance ($)": f"{bal:.2f}"})

        # Calculate spending for the chart
        spent = sum(
            abs(entry["amount"]) for entry in cat_obj.ledger if entry["amount"] < 0
        )
        if spent > 0:
            withdrawal_data.append({"Category": name, "Amount Spent": spent})

    # Render Table
    if balance_data:
        df_balances = pd.DataFrame(balance_data)
        st.dataframe(df_balances, use_container_width=True, hide_index=True)
    else:
        st.info("No categories available.")

    st.subheader("Spending Chart")
    if withdrawal_data:
        df_spent = pd.DataFrame(withdrawal_data).set_index("Category")
        st.bar_chart(df_spent)
    else:
        st.caption("Chart will populate once withdrawals are logged.")
