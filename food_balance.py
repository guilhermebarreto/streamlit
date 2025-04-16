import streamlit as st
import pandas as pd
import plotly.express as px

# Configurar a página
st.set_page_config(page_title="Food - Production, Importation and Exportation", layout="wide")

# Título geral do dashboard
st.title("Food - Production, Importation and Exportation")

# Função para carregar os dados
@st.cache_data
def load_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRvH2wqS3SayJ6sMG3j96qK6-Iud4jbgX44DWMEPEN8OAOJXjGCs2tGYcXzl649ioq12_Ix06UDoFOh/pub?output=csv"
    df = pd.read_csv(url)

    # Remover espaços extras dos nomes das colunas
    df.columns = df.columns.str.strip()

    # Converter a coluna "Value" para número
    df["Value"] = pd.to_numeric(df["Value"], errors="coerce").fillna(0)

    return df

# Carregar dados
df = load_data()

# Filtros com selectbox em colunas
with st.expander("Filters", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        selected_area = st.selectbox("Select Area", ["Selecione..."] + sorted(df["Area"].unique()))
    with col2:
        selected_item = st.selectbox("Select Item", ["Selecione..."] + sorted(df["Item"].unique()))
    with col3:
        selected_element = st.selectbox("Select Element", ["Selecione..."] + sorted(df["Element"].unique()))

# Aplicar filtros
df_filtered = df.copy()

if selected_area != "Selecione...":
    df_filtered = df_filtered[df_filtered["Area"] == selected_area]

if selected_item != "Selecione...":
    df_filtered = df_filtered[df_filtered["Item"] == selected_item]

if selected_element != "Selecione...":
    df_filtered = df_filtered[df_filtered["Element"] == selected_element]

# Gráfico: Top 10 Região
st.markdown("### Region")
top_regions = (
    df_filtered.groupby("Area")["Value"]
    .sum()
    .reset_index()
    .sort_values(by="Value", ascending=False)
    .head(10)
)
region_chart = px.bar(top_regions, x="Area", y="Value", text="Value")
st.plotly_chart(region_chart, use_container_width=True, key="region_chart")

# Gráfico: Balance (Element x Value)
st.markdown("### Balance")
top_balance = (
    df_filtered.groupby("Element")["Value"]
    .sum()
    .reset_index()
    .sort_values(by="Value", ascending=False)
    .head(10)
)
balance_chart = px.bar(top_balance, x="Element", y="Value", text="Value")
st.plotly_chart(balance_chart, use_container_width=True, key="balance_chart")

# Gráfico: Item x Produção (limitado a 10 valores)
st.markdown("### Item")
item_prod_chart = px.bar(
    df_filtered.groupby("Item")["Value"]
    .sum()
    .reset_index()
    .sort_values(by="Value", ascending=False)
    .head(10),
    x="Item", y="Value", text="Value"
)
st.plotly_chart(item_prod_chart, use_container_width=True, key="item_prod_chart")

# Gráfico: Timeline de Produção (Date x Value com quebra anual)
st.markdown("### Timeline")
df_filtered["Date"] = pd.to_datetime(df_filtered["Date"], errors="coerce")
df_filtered["Year"] = df_filtered["Date"].dt.year  # Quebra por ano

timeline_df = df_filtered.groupby(["Year"])["Value"].sum().reset_index()
timeline_chart = px.line(
    timeline_df,
    x="Year", y="Value",
    line_shape="spline",
    markers=True
)
timeline_chart.update_layout( xaxis_title="Year", yaxis_title="Value")
st.plotly_chart(timeline_chart, use_container_width=True, key="timeline_chart")
