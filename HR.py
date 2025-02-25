import streamlit as st
import pandas as pd
import sqlite3
from PIL import Image

# Load Logo
logo = Image.open("milv.png")

# Initialize Streamlit App
st.set_page_config(page_title="MILV HR Dashboard", layout="wide")

# Sidebar Styling
st.sidebar.image(logo, width=150)
st.sidebar.header("Filters")

# Load Data from SQLite
@st.cache_data
def load_data():
    conn = sqlite3.connect("HR.db")
    hr_data = pd.read_sql("SELECT * FROM hr_data", conn)
    provider_data = pd.read_sql("SELECT * FROM provider_data", conn)
    directory_data = pd.read_sql("SELECT * FROM directory_data", conn)
    terminated_data = pd.read_sql("SELECT * FROM terminated_data", conn)
    conn.close()

    # Standardize column names
    for df in [hr_data, provider_data, directory_data, terminated_data]:
        df.columns = df.columns.str.strip().str.lower().str.replace("\n", "_", regex=True)
    
    # Rename "milv radiologist" to "name" in terminated_data if applicable
    if "milv_radiologist" in terminated_data.columns:
        terminated_data.rename(columns={"milv_radiologist": "name"}, inplace=True)
    
    return hr_data, provider_data, directory_data, terminated_data

hr_data, provider_data, directory_data, terminated_data = load_data()

# Sidebar Filters
name_filter = st.sidebar.text_input("Search by Name")
category_filter = st.sidebar.multiselect("Filter by Category", hr_data['category'].dropna().unique())
employment_type_filter = st.sidebar.multiselect("Employment Type", hr_data['employment_type'].dropna().unique())
location_filter = st.sidebar.multiselect("Location", hr_data['location'].dropna().unique())

# Tabs for Active vs Terminated Employees
tab1, tab2 = st.tabs(["Active Employees", "Terminated Employees"])

with tab1:
    st.subheader("Active Employee Directory")
    active_data = hr_data[hr_data['terminated'] == False]
    
    # Apply Filters
    if name_filter:
        active_data = active_data[active_data['name'].str.contains(name_filter, case=False, na=False)]
    if category_filter:
        active_data = active_data[active_data['category'].isin(category_filter)]
    if employment_type_filter:
        active_data = active_data[active_data['employment_type'].isin(employment_type_filter)]
    if location_filter:
        active_data = active_data[active_data['location'].isin(location_filter)]
    
    st.dataframe(active_data)

with tab2:
    st.subheader("Terminated Employee Directory")
    if "name" in terminated_data.columns:
        terminated_data_filtered = terminated_data.copy()
        
        if name_filter:
            terminated_data_filtered = terminated_data_filtered[terminated_data_filtered['name'].str.contains(name_filter, case=False, na=False)]
        
        st.dataframe(terminated_data_filtered)
    else:
        st.warning("The 'name' column is missing from the Terminated Employees dataset.")

# HR Metrics
st.subheader("HR Metrics")
col1, col2 = st.columns(2)

with col1:
    st.metric("Total Employees", len(hr_data))
    st.metric("Active Employees", len(hr_data[hr_data['terminated'] == False]))

with col2:
    st.metric("Terminated Employees", len(hr_data[hr_data['terminated'] == True]))
    st.metric("Turnover Rate", f"{(len(hr_data[hr_data['terminated'] == True])/len(hr_data) * 100):.2f}%")
