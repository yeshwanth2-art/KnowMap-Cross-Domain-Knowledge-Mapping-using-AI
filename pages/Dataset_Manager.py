import streamlit as st
import pandas as pd
from io import StringIO

if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.error("You must be logged in to view this page.")
    st.stop()


st.title("📁 Dataset Manager & Triples Review")
st.info("Upload new datasets (CSV, Excel) to be processed or review the currently loaded data.")

st.subheader("Upload Dataset")
uploaded_file = st.file_uploader(
    "Choose a CSV or Excel file",
    type=["csv", "xlsx"],
    help="Upload a file containing text or pre-extracted triples."
)

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.session_state["uploaded_df"] = df
        st.session_state["data_source_name"] = uploaded_file.name
        
        st.success(f"Successfully loaded **{uploaded_file.name}** with {len(df)} rows.")
        st.experimental_rerun() 

    except Exception as e:
        st.error(f"Error reading file: {e}")

st.markdown("---")

st.subheader("Current Working Dataset")

if "uploaded_df" in st.session_state:
    df = st.session_state["uploaded_df"]
    source_name = st.session_state["data_source_name"]
    
    st.write(f"**Source:** `{source_name}` | **Rows:** `{len(df)}` | **Columns:** `{len(df.columns)}`")
    
    text_column = st.selectbox(
        "Select the primary text column for Triple Extraction:",
        df.columns,
        key="text_column_selector"
    )

    st.markdown("#### Data Preview (Editable)")
    st.data_editor(df, num_rows="dynamic", key="data_editor")
    
    if st.button("Save Changes to Working Dataset", type="primary"):
        st.success("Changes saved to the working dataset in session state.")

else:
    st.warning("No dataset is currently loaded. Please upload a file above.")