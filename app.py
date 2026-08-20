import streamlit as st
import pandas as pd

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

    def transfer(self, amount, receiver):
        if self.withdraw(amount, f"Transfer to {receiver.name}"):
            receiver.deposit(amount, f"Transfer from {self.name}")
            return True
        return False

    def check_funds(self, amount):
        return float(amount) <= self.get_balance()

st.set_page_config(page_title="Budget App", layout="wide")

if 'categories' not in st.session_state:
    st.session_state.categories = {
        "Food": Category("Food"),
        "Clothing": Category("Clothing"),
        "Entertainment": Category("Entertainment")
    }

st.title("Financial Ledger & Budget App")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Transactions")
    selected_cat = st.selectbox("Select Category", list(st.session_state.categories.keys()))
    action = st.radio("Action", ["Deposit", "Withdraw"])
    amount = st.number_input("Amount", min_value=0.01, step=10.0)
    desc = st.text_input("Description (Optional)")

    if st.button("Execute Transaction"):
        target = st.session_state.categories[selected_cat]
        if action == "Deposit":
            target.deposit(amount, desc)
            st.success(f"Deposited ${amount} into {selected_cat}")
        else:
            if target.withdraw(amount, desc):
                st.success(f"Withdrew ${amount} from {selected_cat}")
            else:
                st.error("Insufficient funds.")
        st.rerun()

with col2:
    st.subheader("Financial Overview")
    
    balances = {name: cat.get_balance() for name, cat in st.session_state.categories.items()}
    st.dataframe(pd.DataFrame(list(balances.items()), columns=["Category", "Balance"]), hide_index=True)

    st.divider()

    st.subheader("Spending Distribution")
    withdrawals = {}
    for name, cat in st.session_state.categories.items():
        spent = sum(abs(entry["amount"]) for entry in cat.ledger if entry["amount"] < 0)
        withdrawals[name] = spent
    
    if sum(withdrawals.values()) > 0:
        st.bar_chart(pd.DataFrame(list(withdrawals.items()), columns=["Category", "Amount Spent"]).set_index("Category"))
    else:
        st.info("No withdrawal data yet.")