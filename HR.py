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
    
    # Remove timestamps from date columns
    date_columns = ["hire_date", "rehire_date", "termination_date"]
    for col in date_columns:
        if col in hr_data.columns:
            hr_data[col] = pd.to_datetime(hr_data[col], errors='coerce').dt.date
    
    # Standardize category values (e.g., ensure "Partner" is consistent)
    if "category" in hr_data.columns:
        hr_data["category"] = hr_data["category"].str.strip().str.lower().str.replace(r"\[|\]", "", regex=True).str.title()
    
    return hr_data, provider_data, directory_data, terminated_data

hr_data, provider_data, directory_data, terminated_data = load_data()

# HR Metrics - Meaningful insights for HR Partner
st.subheader("HR Metrics")
col1, col2, col3 = st.columns(3)

total_employees = len(hr_data)
active_employees = len(hr_data[hr_data['terminated'] == False])
terminated_employees = len(hr_data[hr_data['terminated'] == True])
turnover_rate = (terminated_employees / total_employees * 100) if total_employees > 0 else 0

with col1:
    st.metric("Total Employees", total_employees)
    st.metric("Active Employees", active_employees)

with col2:
    st.metric("Terminated Employees", terminated_employees)
    st.metric("Turnover Rate", f"{turnover_rate:.2f}%")

if "hire_date" in hr_data.columns and "termination_date" in hr_data.columns:
    recent_hires = len(hr_data[pd.to_datetime(hr_data['hire_date'], errors='coerce') >= pd.to_datetime("2024-01-01")])
    recent_terminations = len(hr_data[pd.to_datetime(hr_data['termination_date'], errors='coerce') >= pd.to_datetime("2024-01-01")])
    with col3:
        st.metric("New Hires in 2024", recent_hires)
        st.metric("Terminations in 2024", recent_terminations)

# Sidebar Filters
name_filter = st.sidebar.text_input("Search by Name")
category_filter = st.sidebar.multiselect("Filter by Category", sorted(hr_data['category'].dropna().unique()))
employment_type_filter = st.sidebar.multiselect("Employment Type", sorted(hr_data['employment_type'].dropna().unique()))
status_filter = st.sidebar.multiselect("Employment Status (FT/PT)", sorted(hr_data['status_ft/pt'].dropna().unique()))
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
