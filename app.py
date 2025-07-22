import streamlit as st
import pandas as pd
import os
from datetime import datetime

# -----------------------
# CONFIGURATION
# -----------------------
st.set_page_config(page_title="Tracker", page_icon="💰", layout="centered")
DATA_FILE = "finance_data.csv"
PASSWORD = "Admin123"

# -----------------------
# DATA HANDLING
# -----------------------
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=["Paid_By", "Amount", "Split_Type", "Description", "Time"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

def add_transaction(person, amount, split_type, description):
    df = load_data()
    new_row = pd.DataFrame({
        "Paid_By": [person],
        "Amount": [amount],
        "Split_Type": [split_type],
        "Description": [description if description else ""],
        "Time": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    })
    df = pd.concat([df, new_row], ignore_index=True)
    save_data(df)

def calculate_net_balance():
    df = load_data()
    if df.empty:
        return 0

    net_balance = 0  # Positive → Minhaz owes Mannat; Negative → Mannat owes Minhaz

    for _, row in df.iterrows():
        payer = row["Paid_By"]
        amt = row["Amount"]
        split = row["Split_Type"]

        if split == "Split Half":
            if payer == "Mannat":
                net_balance += amt / 2
            else:
                net_balance -= amt / 2
        else:  # Full
            if payer == "Mannat":
                net_balance += amt
            else:
                net_balance -= amt

    return net_balance

def clear_balances():
    save_data(pd.DataFrame(columns=["Paid_By", "Amount", "Split_Type", "Description", "Time"]))

def delete_selected(indices):
    df = load_data()
    df = df.drop(indices).reset_index(drop=True)
    save_data(df)

# -----------------------
# USER PANEL
# -----------------------
st.title("💰 Tracker")

st.subheader("Add a Transaction")
amount = st.number_input("Enter Amount (₹)", min_value=1, step=1)
paid_by = st.radio("Who Paid?", ["Mannat", "Minhaz"])
split_type = st.selectbox("Split Type", ["Split Half", "Full"])
description = st.text_input("Description (Optional)")

if st.button("Submit Transaction"):
    add_transaction(paid_by, amount, split_type, description)
    st.success(f"✅ {paid_by} paid ₹{amount} ({split_type}){' - ' + description if description else ''}")

# -----------------------
# ADMIN PANEL (PASSWORD PROTECTED)
# -----------------------
st.markdown("---")
st.subheader("🔐 Admin Panel")
password = st.text_input("Enter Admin Password", type="password")

if password == PASSWORD:
    st.success("Access Granted ✅")

    df = load_data()

    # Show Tables
    st.write("### 📌 Transactions Overview")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Mannat")
        mannat_df = df[df["Paid_By"] == "Mannat"][["Amount", "Split_Type", "Description", "Time"]]
        st.table(mannat_df if not mannat_df.empty else pd.DataFrame({"Amount": [], "Split_Type": [], "Description": [], "Time": []}))

    with col2:
        st.subheader("Minhaz")
        minhaz_df = df[df["Paid_By"] == "Minhaz"][["Amount", "Split_Type", "Description", "Time"]]
        st.table(minhaz_df if not minhaz_df.empty else pd.DataFrame({"Amount": [], "Split_Type": [], "Description": [], "Time": []}))

    # Show Net Balance
    st.write("### Current Balance")
    net_balance = calculate_net_balance()
    if abs(net_balance) < 1e-2:
        st.info("All Settled! 🎉")
    elif net_balance > 0:
        st.warning(f"💸 Minhaz should pay Mannat: ₹{net_balance:.2f}")
    else:
        st.warning(f"💸 Mannat should pay Minhaz: ₹{abs(net_balance):.2f}")

    # Selective Deletion (Mark Selected as Paid)
    if not df.empty:
        st.write("### ✅ Mark Selected Transactions as Paid (Delete)")
        selected_indices = st.multiselect(
            "Select transactions to delete (mark as paid):",
            df.index,
            format_func=lambda x: f"{df.loc[x, 'Paid_By']} | ₹{df.loc[x, 'Amount']} | {df.loc[x, 'Description']} | {df.loc[x, 'Time']}"
        )
        if st.button("Delete Selected Transactions"):
            delete_selected(selected_indices)
            st.success("✅ Selected transactions deleted (marked as paid)!")

    # Clear All Button
    if st.button("Clear All Balances (Mark All as Paid)"):
        clear_balances()
        st.success("✅ All balances cleared!")

elif password != "":
    st.error("❌ Wrong Password")
