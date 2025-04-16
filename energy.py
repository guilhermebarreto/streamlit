import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Page config
st.set_page_config(page_title="Energy Production - International Energy Agency", layout="wide")

# Title
st.title("Energy Production - International Energy Agency")

# Load data
URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSj7qktCSDEnRr4rApiv_etOQ6fys3KEWHPOhSo3-St9KHTmV7uyDG_qgH_9NJe4FkMe03x1uLQB1nF/pub?output=csv"
df = pd.read_csv(URL)

# Data treatment
df = df[~df['Country'].str.contains(r"(Total|OEDC|OECD)", regex=True, na=False)]
df = df[df['Balance'].str.contains("Net Electricity Production", na=False)]
df['Value'] = pd.to_numeric(df['Value'], errors='coerce').fillna(0)
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df['Year'] = df['Date'].dt.year

# Filters
with st.expander("Filters", expanded=True):
    col1, col2, col3 = st.columns(3)
    countries = sorted(df["Country"].dropna().unique())
    products = sorted(df["Product"].dropna().unique())
    years = sorted(df["Year"].dropna().unique())

    selected_country = col1.selectbox("Select Country (optional)", options=["All"] + countries, index=0)
    selected_product = col2.selectbox("Select Product (optional)", options=["All"] + products, index=0)
    selected_year = col3.selectbox("Select Year (optional)", options=["All"] + [str(y) for y in years], index=0)

# Filter logic
df_filtered = df.copy()
if selected_country != "All":
    df_filtered = df_filtered[df_filtered["Country"] == selected_country]
if selected_product != "All":
    df_filtered = df_filtered[df_filtered["Product"] == selected_product]
if selected_year != "All":
    df_filtered = df_filtered[df_filtered["Year"] == int(selected_year)]

# Format values in millions with comma as decimal separator
def format_mi(value):
    return f"{value / 1e6:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".") + " Mi"

### Chart 1 - Country
country_group = df_filtered.groupby("Country")["Value"].sum().reset_index().sort_values(by="Value", ascending=False).head(10)
country_group["Formatted"] = country_group["Value"].apply(format_mi)

fig_country = px.bar(
    country_group,
    x="Country",
    y="Value",
    title="Top Countries in Energy Production",
    text="Formatted"
)
fig_country.update_traces(textposition="outside")
fig_country.update_layout(yaxis_title="Value", xaxis_title="Country", yaxis_tickformat=",")
st.plotly_chart(fig_country, use_container_width=True)

### Chart 2 - Product
product_group = df_filtered.groupby("Product")["Value"].sum().reset_index().sort_values(by="Value", ascending=False).head(10)
product_group["Formatted"] = product_group["Value"].apply(format_mi)

fig_product = px.bar(
    product_group,
    x="Product",
    y="Value",
    title="Top Products in Energy Production",
    text="Formatted"
)
fig_product.update_traces(textposition="outside")
fig_product.update_layout(yaxis_title="Value", xaxis_title="Product", yaxis_tickformat=",")
st.plotly_chart(fig_product, use_container_width=True)

### Chart 3 - Timeline
timeline_group = df_filtered.groupby("Year")["Value"].sum().reset_index()
timeline_group["Formatted"] = timeline_group["Value"].apply(format_mi)

fig_timeline = px.line(
    timeline_group,
    x="Year",
    y="Value",
    title="Energy Production Over Time",
    text="Formatted",
)
fig_timeline.update_traces(textposition="top center", mode="lines+markers")
fig_timeline.update_layout(
    yaxis_title="Value",
    xaxis_title="Year",
    yaxis_tickformat=",",
    hovermode="x unified"
)
fig_timeline.update_traces(line_shape="spline")
st.plotly_chart(fig_timeline, use_container_width=True)
