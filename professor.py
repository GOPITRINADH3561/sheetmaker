import streamlit as st
import pandas as pd
import os
import io
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# === Load saved data ===
if 'professors' not in st.session_state:
    if os.path.exists("data.csv"):
        st.session_state.professors = pd.read_csv("data.csv").to_dict(orient="records")
    else:
        st.session_state.professors = []

st.title("📚 Professor Assistantship Tracker")

# === Excel Import ===
st.sidebar.subheader("📤 Import Excel (.xlsx)")
uploaded_file = st.sidebar.file_uploader("Choose Excel file", type=["xlsx"])

if uploaded_file:
    try:
        df_uploaded = pd.read_excel(uploaded_file)
        added_count = 0

        for _, row in df_uploaded.iterrows():
            name = str(row.get("Name", "")).strip()
            email = str(row.get("Email", "")).strip().lower()
            dept = str(row.get("Department", "")).strip()
            status = str(row.get("Status", "Applied")).strip()
            chance = str(row.get("Chance", "❌ Not an Opportunity")).strip()

            if email.endswith("@uh.edu") and not any(p['Email'].lower() == email for p in st.session_state.professors):
                st.session_state.professors.append({
                    "Name": name,
                    "Email": email,
                    "Department": dept,
                    "Status": status if status in ["Applied", "Replied"] else "Applied",
                    "Chance": chance if chance in ["✅ Opportunity", "❌ Not an Opportunity"] else "❌ Not an Opportunity"
                })
                added_count += 1

        st.sidebar.success(f"✅ Imported {added_count} new professors.")
    except Exception as e:
        st.sidebar.error(f"❌ Failed to read file: {e}")

# === Add Form ===
st.sidebar.header("Add Professor Manually")
with st.sidebar.form("add_professor_form", clear_on_submit=True):
    name = st.text_input("👤 Name")
    email = st.text_input("📧 Email (must end with @uh.edu)")
    dept = st.text_input("🏛️ Department")

    submitted = st.form_submit_button("➕ Add Professor")

    if submitted:
        email_lower = email.lower()
        if not name or not email or not dept:
            st.sidebar.error("❌ All fields are required.")
        elif not email_lower.endswith("@uh.edu"):
            st.sidebar.error("❌ Email must end with '@uh.edu'")
        elif any(p['Email'].lower() == email_lower for p in st.session_state.professors):
            st.sidebar.error(f"❌ Professor with email `{email}` already exists!")
        else:
            st.session_state.professors.append({
                "Name": name,
                "Email": email,
                "Department": dept,
                "Status": "Applied",
                "Chance": "❌ Not an Opportunity"
            })
            st.sidebar.success(f"✅ `{name}` added successfully!")

# === Display and Edit with AgGrid ===
st.subheader("📋 Current List of Professors")

if st.session_state.professors:
    df = pd.DataFrame(st.session_state.professors)

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(sortable=True, filter=True, editable=False)
    gb.configure_column("Status", editable=True, cellEditor='agSelectCellEditor',
                        cellEditorParams={"values": ["Applied", "Replied"]})
    gb.configure_column("Chance", editable=True, cellEditor='agSelectCellEditor',
                        cellEditorParams={"values": ["✅ Opportunity", "❌ Not an Opportunity"]})
    gb.configure_selection('single')

    grid_options = gb.build()

    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        fit_columns_on_grid_load=True,
        enable_enterprise_modules=False,
        height=400,
        theme='streamlit',  # or 'alpine'
    )

    # Save edited table back to session
    updated_df = grid_response['data']
    st.session_state.professors = updated_df.to_dict(orient="records")
    updated_df.to_csv("data.csv", index=False)

    # Export to Excel
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        updated_df.to_excel(writer, index=False, sheet_name='Professors')

    st.download_button(
        label="📥 Download as Excel",
        data=buffer.getvalue(),
        file_name="professor_list.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("No professors added yet.")
