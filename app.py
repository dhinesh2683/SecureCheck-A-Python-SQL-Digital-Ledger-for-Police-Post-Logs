import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# -------------------------
# Page Title and Styling
# -------------------------
st.set_page_config(page_title="🚔 SecureCheck Dashboard", layout="wide")
st.markdown("""
    <style>
        .main {background-color: #f7f9fb;}
        .stTextInput>div>div>input {
            background-color: #ffffff;
            padding: 10px;
            border-radius: 8px;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🚔 SecureCheck: Police Stop Log & Insights")
st.markdown("---")

# -------------------------
# Database Connection
# -------------------------
username = 'root'
password = 'dhinesh'
host = 'localhost'
port = '3306'
database = 'traffic_logs'

engine = create_engine(f'mysql+mysqlconnector://{username}:{password}@{host}:{port}/{database}')

# -------------------------
# Load Data
# -------------------------
@st.cache_data
def load_data():
    query = "SELECT * FROM traffic_stops"
    return pd.read_sql(query, engine)

df = load_data()

# -------------------------
# Filter Section
# -------------------------
st.sidebar.header("🔍 Filter Options")

selected_country = st.sidebar.multiselect("Country", options=sorted(df['country_name'].dropna().unique()))
selected_violation = st.sidebar.multiselect("Violation", options=sorted(df['violation'].dropna().unique()))
selected_gender = st.sidebar.multiselect("Gender", options=sorted(df['driver_gender'].dropna().unique()))
selected_race = st.sidebar.multiselect("Race", options=sorted(df['driver_race'].dropna().unique()))
selected_search = st.sidebar.selectbox("Was a Search Conducted?", ["All", "True", "False"])
selected_drug = st.sidebar.selectbox("Drug Related Stop?", ["All", "True", "False"])

# Apply Filters
filtered_df = df.copy()
if selected_country:
    filtered_df = filtered_df[filtered_df['country_name'].isin(selected_country)]
if selected_violation:
    filtered_df = filtered_df[filtered_df['violation'].isin(selected_violation)]
if selected_gender:
    filtered_df = filtered_df[filtered_df['driver_gender'].isin(selected_gender)]
if selected_race:
    filtered_df = filtered_df[filtered_df['driver_race'].isin(selected_race)]
if selected_search != "All":
    filtered_df = filtered_df[filtered_df['search_conducted'] == selected_search]
if selected_drug != "All":
    filtered_df = filtered_df[filtered_df['drugs_related_stop'] == selected_drug]

# -------------------------
# Display Filtered Data
# -------------------------
st.subheader("📄 Filtered Police Stop Records")
st.dataframe(filtered_df, use_container_width=True)

# -------------------------
# Insights Section
# -------------------------
st.markdown("---")
st.header("📊 Advanced Insights")

query_option = st.selectbox("Select a Query to Run", [
    "Top 5 Most Frequent Search Types",
    "Top 5 Violations",
    "Arrest Rate by Gender",
    "Drug-Related Stops by Country"
])

if st.button("Run Query"):
    if query_option == "Top 5 Most Frequent Search Types":
        result = df['search_type'].value_counts().head(5).reset_index()
        result.columns = ['Search Type', 'Count']
        st.dataframe(result)

    elif query_option == "Top 5 Violations":
        result = df['violation'].value_counts().head(5).reset_index()
        result.columns = ['Violation', 'Count']
        st.dataframe(result)

    elif query_option == "Arrest Rate by Gender":
        arrest_rate = df.groupby('driver_gender')['is_arrested'].apply(lambda x: (x == 'True').mean() * 100).reset_index()
        arrest_rate.columns = ['Gender', 'Arrest Rate (%)']
        st.dataframe(arrest_rate)

    elif query_option == "Drug-Related Stops by Country":
        result = df[df['drugs_related_stop'] == 'True']['country_name'].value_counts().reset_index()
        result.columns = ['Country', 'Drug-Related Stops']
        st.dataframe(result)