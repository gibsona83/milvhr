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

# Load Data
@st.cache_data
def load_data():
    hr_data = pd.read_csv("HRdata.csv")
    provider_data = pd.read_excel("MILV - Provider Worksheet.xlsx")
    directory_data = pd.read_excel("MILV HR Directory.xlsx")
    terminated_data = pd.read_excel("Terminated Radiologists.xlsx")
    
    # Standardize column names (remove spaces, lowercase, and fix newlines)
    hr_data.columns = hr_data.columns.str.strip().str.lower().str.replace("\n", "_")
    provider_data.columns = provider_data.columns.str.strip().str.lower().str.replace("\n", "_")
    directory_data.columns = directory_data.columns.str.strip().str.lower().str.replace("\n", "_")
    terminated_data.columns = terminated_data.columns.str.strip().str.lower().str.replace("\n", "_")
    
    # Rename "milv radiologist" to "name" in terminated_data
    if "milv radiologist" in terminated_data.columns:
        terminated_data.rename(columns={"milv radiologist": "name"}, inplace=True)
    
    return hr_data, provider_data, directory_data, terminated_data

hr_data, provider_data, directory_data, terminated_data = load_data()

# Sidebar Filters
name_filter = st.sidebar.text_input("Search by Name")
category_filter = st.sidebar.multiselect("Filter by Category", hr_data['category'].dropna().unique())

# Tabs for Active vs Terminated Employees
tab1, tab2 = st.tabs(["Active Employees", "Terminated Employees"])

with tab1:
    st.subheader("Active Employee Directory")
    active_data = hr_data[hr_data['terminated'] == False]
    if name_filter:
        active_data = active_data[active_data['name'].str.contains(name_filter, case=False, na=False)]
    if category_filter:
        active_data = active_data[active_data['category'].isin(category_filter)]
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
