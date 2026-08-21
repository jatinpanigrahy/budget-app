import streamlit as st
import pandas as pd
import altair as alt


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


st.set_page_config(
    page_title="Budget App", page_icon="assets/favicon.svg", layout="wide"
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
        font-weight: 400;
        letter-spacing: -0.01em;
    }
    
    [data-testid="stElementToolbar"], footer, header {
        display: none !important;
    }
    
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }

    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        color: #e6edf3 !important;
        border-radius: 6px !important;
    }

    div.stButton > button {
        background-color: #1f6feb !important;
        color: white !important;
        border: 1px solid rgba(240, 246, 252, 0.1) !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease;
    }
    
    div.stButton > button:hover {
        background-color: #388bfd !important;
        border-color: #8b949e !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 2.4rem !important;
        font-weight: 600 !important;
        color: #58a6ff !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.85rem !important;
        color: #8b949e !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    [data-testid="stTable"] {
        background-color: #161b22;
        border-radius: 6px;
        overflow: hidden;
        border: 1px solid #30363d;
    }
    
    [data-testid="stTable"] th {
        background-color: #0d1117 !important;
        color: #8b949e !important;
        border-bottom: 1px solid #30363d !important;
        font-weight: 500;
    }
    
    [data-testid="stTable"] td {
        border-bottom: 1px solid #21262d !important;
        color: #c9d1d9;
    }
    
    [data-testid="stExpander"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 6px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "categories" not in st.session_state:
    st.session_state.categories = {
        "Food": Category("Food"),
        "Housing": Category("Housing"),
        "Transport": Category("Transport"),
    }

if "focus_category" not in st.session_state:
    st.session_state.focus_category = None

active_data = st.session_state.categories

st.title("Budget App")
st.markdown("""
A minimal application to track financial deposits, withdrawals, and inter-category transfers.

**Quick Start:** Use the default categories, or create your own below to begin tracking your finances.
""")
st.divider()

col_transact, col_data = st.columns([1, 1.5])

with col_transact:
    st.subheader("Create Categories")
    col_cat_input, col_cat_btn = st.columns([3, 1])
    with col_cat_input:
        new_cat = st.text_input(
            "Name", placeholder="e.g. Subscriptions", label_visibility="collapsed"
        ).strip()
    with col_cat_btn:
        if st.button("Add", use_container_width=True):
            if new_cat and new_cat not in active_data:
                active_data[new_cat] = Category(new_cat)
                st.session_state.focus_category = new_cat
                st.success("Added.")
                st.rerun()
            elif new_cat in active_data:
                st.error("Exists.")

    st.markdown("---")
    st.subheader("Transactions")

    cat_options = list(active_data.keys())
    if not cat_options:
        st.warning("Create a category first.")
    else:
        # Dynamic Index Resolution
        default_index = 0
        if st.session_state.focus_category in cat_options:
            default_index = cat_options.index(st.session_state.focus_category)

        selected_cat = st.selectbox("Source Category", cat_options, index=default_index)
        action = st.radio("Type", ["Deposit", "Withdraw", "Transfer"], horizontal=True)

        target_cat = None
        if action == "Transfer":
            target_options = [cat for cat in cat_options if cat != selected_cat]
            if not target_options:
                st.warning("Requires a second category for transfer.")
            else:
                target_cat = st.selectbox("Target Category", target_options)

        amount = st.number_input("Amount (₹)", value=1.0, step=100.0, format="%.2f")

        if action in ["Deposit", "Withdraw"]:
            desc = st.text_input("Description (Optional)")
        else:
            desc = ""

        if st.button("Submit"):
            if amount <= 0:
                st.error(
                    "Execution blocked: Amount must be strictly greater than zero."
                )
            else:
                cat_obj = active_data[selected_cat]
                st.session_state.focus_category = selected_cat

                if action == "Deposit":
                    cat_obj.deposit(amount, desc)
                    st.success("Deposited.")
                    st.rerun()

                elif action == "Withdraw":
                    if cat_obj.withdraw(amount, desc):
                        st.success("Withdrawn.")
                        st.rerun()
                    else:
                        st.error("Insufficient funds.")

                elif action == "Transfer":
                    if not target_cat:
                        st.error("Target missing.")
                    else:
                        receiver_obj = active_data[target_cat]
                        if cat_obj.transfer(amount, receiver_obj):
                            st.success("Transferred.")
                            st.rerun()
                        else:
                            st.error("Insufficient funds.")

with col_data:
    st.subheader("Overview")

    active_categories = {
        name: cat for name, cat in active_data.items() if len(cat.ledger) > 0
    }

    if not active_categories:
        st.info("No data yet. Log a transaction to view the overview.")
    else:
        # Algorithmic Sorting: Extract Top 4 by Balance
        sorted_cats = sorted(
            active_categories.items(), key=lambda x: x[1].get_balance(), reverse=True
        )
        display_names = [name for name, _ in sorted_cats][:4]

        metric_cols = st.columns(len(display_names))
        for index, name in enumerate(display_names):
            with metric_cols[index]:
                st.metric(
                    label=name, value=f"₹{active_categories[name].get_balance():.2f}"
                )

        audit_trail = []
        for name, cat in active_categories.items():
            for entry in cat.ledger:
                amt = entry["amount"]
                sign = "+" if amt > 0 else "\u2212"
                formatted_amount = f"{sign}\u00a0₹{abs(amt):.2f}"

                audit_trail.append(
                    {
                        "Category": name,
                        "Type": "Deposit" if amt > 0 else "Withdrawal",
                        "Amount": formatted_amount,
                        "Description": entry["description"]
                        if entry["description"].strip() != ""
                        else "N/A",
                    }
                )

        with st.expander("Transaction Log", expanded=True):
            if audit_trail:
                st.table(audit_trail[::-1])
            else:
                st.info("Log empty.")

        withdrawal_data = {}
        total_spent = 0
        for name, cat in active_categories.items():
            spent = sum(
                abs(entry["amount"]) for entry in cat.ledger if entry["amount"] < 0
            )
            if spent > 0:
                withdrawal_data[name] = spent
                total_spent += spent

        if withdrawal_data and total_spent > 0:
            st.subheader("Relative Spending Chart")

            pct_data = [
                {"Category": k, "Percentage": (v / total_spent) * 100}
                for k, v in withdrawal_data.items()
            ]
            df_chart = pd.DataFrame(pct_data)

            chart = (
                alt.Chart(df_chart)
                .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
                .encode(
                    x=alt.X(
                        "Category:N",
                        axis=alt.Axis(
                            labelAngle=0,
                            labelFont="Inter",
                            titleFont="Inter",
                            labelColor="#8b949e",
                            titleColor="#8b949e",
                        ),
                    ),
                    y=alt.Y(
                        "Percentage:Q",
                        scale=alt.Scale(domain=[0, 100]),
                        title="Percentage of Total Spent (%)",
                        axis=alt.Axis(
                            labelFont="Inter",
                            titleFont="Inter",
                            labelColor="#8b949e",
                            titleColor="#8b949e",
                        ),
                    ),
                    tooltip=["Category", alt.Tooltip("Percentage:Q", format=".1f")],
                    color=alt.value("#58a6ff"),
                )
                .properties(height=350, background="transparent")
            )

            chart = chart.configure_axis(
                labelFont="Inter",
                titleFont="Inter",
                gridColor="#30363d",
                domainColor="#30363d",
            ).configure_view(strokeWidth=0)

            st.altair_chart(chart, use_container_width=True)
