import streamlit as st
import pandas as pd
from PIL import Image

# Load Logo
logo = Image.open("milv.png")

# Initialize Streamlit App
st.set_page_config(page_title="MILV HR Dashboard", layout="wide")

# Sidebar Styling
st.sidebar.image(logo, width=150)
st.sidebar.header("Filters")

# Load Data from CSV
@st.cache_data
def load_data():
    hr_data = pd.read_csv("HRdata.csv")
    provider_data = pd.read_excel("MILV - Provider Worksheet.xlsx")
    directory_data = pd.read_excel("MILV HR Directory.xlsx")
    terminated_data = pd.read_excel("Terminated Radiologists.xlsx")
    
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
status_filter = st.sidebar.multiselect("Employment Status (FT/PT)", hr_data['status_ft/pt'].dropna().unique())
terminated_filter = st.sidebar.radio("Filter by Active/Terminated", ["All", "Active", "Terminated"])

# Apply Filters
filtered_data = hr_data.copy()

if name_filter:
    filtered_data = filtered_data[filtered_data['name'].str.contains(name_filter, case=False, na=False)]
if category_filter:
    filtered_data = filtered_data[filtered_data['category'].isin(category_filter)]
if employment_type_filter:
    filtered_data = filtered_data[filtered_data['employment_type'].isin(employment_type_filter)]
if status_filter:
    filtered_data = filtered_data[filtered_data['status_ft/pt'].isin(status_filter)]
if terminated_filter == "Active":
    filtered_data = filtered_data[filtered_data['terminated'] == False]
elif terminated_filter == "Terminated":
    filtered_data = filtered_data[filtered_data['terminated'] == True]

# Display Filtered Data
st.subheader("Employee Directory")
st.dataframe(filtered_data)

# HR Metrics
st.subheader("HR Metrics")
col1, col2 = st.columns(2)

with col1:
    st.metric("Total Employees", len(hr_data))
    st.metric("Active Employees", len(hr_data[hr_data['terminated'] == False]))

with col2:
    st.metric("Terminated Employees", len(hr_data[hr_data['terminated'] == True]))
    st.metric("Turnover Rate", f"{(len(hr_data[hr_data['terminated'] == True])/len(hr_data) * 100):.2f}%")
