import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTnZDsIFks_sv45WQ5bPai-eNpf7OtGYzaCMprM0cl_Ln8EBUvEwrL6u-Ci0K8MNWglVzZ1w4Y-eJ1A/pub?output=csv"
df = pd.read_csv(url)

# Clean and convert Index column
df_clean = df.dropna(subset=["Index"])
df_clean["Index"] = df_clean["Index"].replace({',': '.'}, regex=True)
df_clean["Index"] = pd.to_numeric(df_clean["Index"], errors='coerce')
df_clean = df_clean.dropna(subset=["Index"])

# Filters (select boxes) in three columns
st.title("Mobile - Connectivity Index")

st.header("Filters")
col1, col2, col3 = st.columns(3)
with col1:
    region = st.selectbox('Select a region:', ['None'] + list(df_clean['Region'].unique()))
with col2:
    cluster = st.selectbox('Select a cluster:', ['None'] + list(df_clean['Cluster'].unique()))
with col3:
    year = st.selectbox('Select a year:', ['None'] + list(df_clean['Year'].unique()))

# Data filtering
if region == 'None' and cluster == 'None' and year == 'None':
    df_filtered = df_clean
else:
    df_filtered = df_clean[
        (df_clean['Region'] == region if region != 'None' else True) &
        (df_clean['Cluster'] == cluster if cluster != 'None' else True) &
        (df_clean['Year'] == year if year != 'None' else True)
    ]

# Check for data
if df_filtered.empty:
    st.error("There is no valid data for the selected filter combination.")
else:
    # Average index per country
    country_avg_index = df_filtered.groupby('Country')['Index'].mean().sort_values(ascending=False).round(0)

    # Top 10 highest
    top_10_highest = country_avg_index.head(10).sort_values()
    fig1 = px.bar(
        top_10_highest,
        x=top_10_highest.values,
        y=top_10_highest.index,
        orientation='h',
        labels={'x': 'Average Index', 'y': 'Country'},
        title="Top 10 Countries with Highest Index",
        text_auto=True
    )

    # Top 10 lowest
    top_10_lowest = country_avg_index.tail(10).sort_values(ascending=False)
    fig2 = px.bar(
        top_10_lowest,
        x=top_10_lowest.values,
        y=top_10_lowest.index,
        orientation='h',
        labels={'x': 'Average Index', 'y': 'Country'},
        title="Top 10 Countries with Lowest Index",
        color_discrete_sequence=['red'],
        text_auto=True
    )

    # Layout: side-by-side charts
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        st.plotly_chart(fig2, use_container_width=True)

    # --- NEW CHARTS ---

    # Convert coverage columns to numeric
    coverage_cols = ['2G Population Coverage', '3G Population Coverage', '4G Population Coverage', '5G Population Coverage']
    for col in coverage_cols:
        df_filtered[col] = df_filtered[col].replace({',': '.'}, regex=True)
        df_filtered[col] = pd.to_numeric(df_filtered[col], errors='coerce')

    # Coverage charts layout
    with st.container():
        # Chart 1: Yearly evolution (line)
        year_avg = df_filtered.groupby('Year')[coverage_cols].mean().reset_index()
        fig_year = px.line(
            year_avg,
            x='Year',
            y=coverage_cols,
            markers=True,
            labels={'value': 'Average Coverage (%)', 'variable': 'Technology'},
            title='Average Population Coverage by Technology Over the Years'
        )
        st.plotly_chart(fig_year, use_container_width=True)

        # Chart 2: Cluster x Coverage (stacked)
        cluster_avg = df_filtered.groupby('Cluster')[coverage_cols].mean().round(1).reset_index()
        cluster_avg = cluster_avg.sort_values(by='5G Population Coverage', ascending=False)
        cluster_melted = cluster_avg.melt(id_vars='Cluster', value_vars=coverage_cols,
                                          var_name='Technology', value_name='Coverage')

        fig_cluster = px.bar(
            cluster_melted,
            x='Cluster',
            y='Coverage',
            color='Technology',
            title='Average Population Coverage by Cluster and Technology (Sorted by 5G)',
            barmode='stack',
            labels={'Coverage': 'Coverage (%)'},
        )
        st.plotly_chart(fig_cluster, use_container_width=True)
