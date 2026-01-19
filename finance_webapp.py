import streamlit as st
from classes import ExpenseManager

# --- Configuration & Setup ---
DB_PATH = "expenses.db"
CATEGORIES = ["Transporte", "Vivienda", "Misceláneo"]

# Instanciamos el manager
manager = ExpenseManager(DB_PATH)

st.set_page_config(page_title="Finance Manager", page_icon="💰")
st.title("💰 Personal Finance Manager")

if 'df' not in st.session_state:
    st.session_state.df = manager.load_data()

# --- Sidebar: Add New Expense ---
with st.sidebar:
    st.header("Add New Expense")
    with st.form("expense_form", clear_on_submit=True):
        amount = st.number_input("Amount ($)", min_value=0, step=100)
        description = st.text_input("Description")
        category = st.selectbox("Category", CATEGORIES)
        
        submitted = st.form_submit_button("Add Expense")
        
        if submitted:
            st.session_state.df = manager.add_expense(category, description, amount)
            st.toast("Expense added to Database!")

# --- Main Page: Dashboard ---
if st.session_state.df.empty:
    st.info("Start by adding expenses in the sidebar!")
else:
    # 1. Metrics Row
    total_spent, total_count = manager.calculate_metrics(st.session_state.df)
    col1, col2 = st.columns(2)
    col1.metric("Total Spent", f"${total_spent}")
    col2.metric("Total Transactions", len(st.session_state.df))

    # 2. Charts
    st.subheader("Expenses by Category")
    # Grouping by category for visual
    if not st.session_state.df.empty:
        chart_data = manager.get_expenses_by_category(st.session_state.df)
        st.bar_chart(chart_data)

    # 3. Data Table (Editable)
    st.subheader("Transactions Editor")
    
    df_display = st.session_state.df.sort_values(by="Date", ascending=False)
    
    edited_df = st.data_editor(
        df_display,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "id": None, # Best Practice: Hide implementation details (Primary Key) from users
            "Amount": st.column_config.NumberColumn(format="$%d"),
            "Date": st.column_config.DatetimeColumn(format="D MMM YYYY, HH:mm")
        },
        key="main_editor"
    )

    if st.button("💾 Save Changes to DB"):
        st.session_state.df = edited_df
        manager.save_bulk_data(edited_df)
        st.success("Database updated successfully (Schema preserved)!")
        st.rerun()

    # 4. Category Matrix View
    st.subheader("Category Matrix View")
    st.caption("Each column represents a category, showing individual transaction amounts.")
    
    compact_df = manager.get_category_matrix(st.session_state.df, CATEGORIES)
    
    st.dataframe(
        compact_df.style.format("${:.2f}", na_rep=""),
        use_container_width=True,
        hide_index=True 
    )