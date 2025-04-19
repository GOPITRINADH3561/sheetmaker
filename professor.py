import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Assistantship Tracker", layout="wide")
st.title("📚 Professor Assistantship Tracker")

# Custom styles for dropdowns and table
st.markdown(
    """
    <style>
    .dropdown-enhanced select {
        font-size: 13px !important;
        padding: 3px 5px;
        background-color: #f8f9fa;
        border: 1px solid #ccc;
        border-radius: 6px;
        width: 100%;
    }
    .table-header {
        font-weight: bold;
        background-color: #e8f0fe;
        border-bottom: 2px solid #ccc;
        padding: 10px 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state
def init_session():
    if "professors" not in st.session_state:
        st.session_state.professors = pd.DataFrame(columns=[
            "Professor Name", "Professor Mail", "Professor Department", "Status", "Opportunity"
        ])
init_session()

# Sidebar for adding new professor and import/export
with st.sidebar:
    st.header("➕ Add / Manage Professors")
    with st.form("add_prof_form"):
        name = st.text_input("Professor Name")
        email_cols = st.columns([4, 1])
        email_input = email_cols[0].text_input("Professor Mail", placeholder="e.g., jdoe")
        email_cols[1].markdown("<div style='margin-top: 2em;'>@uh.edu</div>", unsafe_allow_html=True)
        email = email_input.strip()
        if email:
            email = email.replace("@uh.edu", "")  # prevent double extension
            email += "@uh.edu"
        dept = st.text_input("Professor Department")
        submitted = st.form_submit_button("Add Professor")

        if submitted:
            # Check for duplicates by email
            if email not in st.session_state.professors['Professor Mail'].values:
                new_prof = pd.DataFrame([[name, email, dept, "Applied", "❌ Not"]],
                                        columns=st.session_state.professors.columns)
                st.session_state.professors = pd.concat([st.session_state.professors, new_prof], ignore_index=True)
                st.success("Professor added successfully!")
            else:
                st.warning("Duplicate entry: Professor with this email already exists.")

    st.markdown("---")
    st.subheader("📤 Export List")
    import io
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        st.session_state.professors.to_excel(writer, index=False, sheet_name='Professors')
        
    st.download_button("Download as Excel", data=excel_buffer.getvalue(), file_name="professors.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    st.markdown("---")
    st.subheader("📥 Import List")
    uploaded_file = st.file_uploader("Upload File", type=["csv", "xlsx"])
    if uploaded_file is not None:
        if uploaded_file.name.endswith('.csv'):
            uploaded_df = pd.read_csv(uploaded_file)
        else:
            uploaded_df = pd.read_excel(uploaded_file)

        st.session_state.professors = pd.concat(
            [st.session_state.professors, uploaded_df]
        ).drop_duplicates(
            subset="Professor Mail", keep="first"
        ).reset_index(drop=True)

        st.success("File imported successfully!")

# Main panel: display the table with styling
if not st.session_state.professors.empty:
    st.markdown("### 📄 Tracked Professors")
    sort_column = st.selectbox("Sort by", st.session_state.professors.columns.tolist(), index=0)
    sort_order = st.radio("Order", ["Ascending", "Descending"], horizontal=True)

    df_sorted = st.session_state.professors.sort_values(by=sort_column, ascending=(sort_order == "Ascending"))

    # Table header
    header_cols = st.columns([3, 3, 3, 2, 2, 1])
    header_cols[0].markdown("<div class='table-header'>Professor Name</div>", unsafe_allow_html=True)
    header_cols[1].markdown("<div class='table-header'>Professor Mail</div>", unsafe_allow_html=True)
    header_cols[2].markdown("<div class='table-header'>Department</div>", unsafe_allow_html=True)
    header_cols[3].markdown("<div class='table-header'>Status</div>", unsafe_allow_html=True)
    header_cols[4].markdown("<div class='table-header'>Opportunity</div>", unsafe_allow_html=True)
    header_cols[5].markdown("<div class='table-header'>Delete</div>", unsafe_allow_html=True)

    # Table rows
    for i, row in df_sorted.iterrows():
        cols = st.columns([3, 3, 3, 2, 2, 1])
        cols[0].markdown(f"**{row['Professor Name']}**")
        cols[1].markdown(f"{row['Professor Mail']}")
        cols[2].write(row['Professor Department'])

        with cols[3]:
            st.markdown("<div class='dropdown-enhanced'>", unsafe_allow_html=True)
            status = st.selectbox(
                label="", label_visibility="collapsed",
                options=["Applied", "Replied"],
                index=["Applied", "Replied"].index(row["Status"]),
                key=f"status_{i}"
            )
            st.markdown("</div>", unsafe_allow_html=True)
            st.session_state.professors.at[i, "Status"] = status

        with cols[4]:
            st.markdown("<div class='dropdown-enhanced'>", unsafe_allow_html=True)
            opportunity = st.selectbox(
                label="", label_visibility="collapsed",
                options=["❌ Not", "✅ Has"],
                index=["❌ Not", "✅ Has"].index(row["Opportunity"]),
                key=f"opportunity_{i}"
            )
            st.markdown("</div>", unsafe_allow_html=True)
            st.session_state.professors.at[i, "Opportunity"] = opportunity

        with cols[5]:
            if st.button("🗑️", key=f"del_{row['Professor Mail']}"):
                st.session_state.professors = st.session_state.professors[st.session_state.professors['Professor Mail'] != row['Professor Mail']]
                st.rerun()
else:
    st.info("No professors added yet. Use the sidebar to begin tracking.")
