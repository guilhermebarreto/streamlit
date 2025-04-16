import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="Streaming Dashboard", layout="wide")

# Carregando os dados
@st.cache_data
def load_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSFXkjO_feKDCw1mnkUELr9CZOZdzso0DyCnnHE_b-g_ljGTKuGw9fs5fq21WovO_L6IDhOEk6zWMzw/pub?output=csv"
    df = pd.read_csv(url)
    return df

df = load_data()

# Filtros no topo com tipos diferentes
col1, col2, col3 = st.columns(3)

with col1:
    type_filter = st.radio("Select Type", options=["All"] + list(df["type"].dropna().unique()), horizontal=True)
    if type_filter == "All":
        type_filter = df["type"].unique()
    else:
        type_filter = [type_filter]

with col2:
    country_filter = st.selectbox("Select Country", options=["All"] + list(df["country"].dropna().unique()))
    if country_filter == "All":
        country_filter = df["country"].unique()
    else:
        country_filter = [country_filter]

with col3:
    release_year_filter = st.slider("Select Release Year", int(df["release_year"].min()), int(df["release_year"].max()), (int(df["release_year"].min()), int(df["release_year"].max())))

# Aplicando filtros
df_filtered = df[
    (df["type"].isin(type_filter)) &
    (df["country"].isin(country_filter)) &
    (df["release_year"].between(release_year_filter[0], release_year_filter[1]))
]

# Métrica principal
st.markdown("### Total Titles")
st.metric(label="Total Titles", value=len(df_filtered))

# Organizando os gráficos
col1, col2 = st.columns([2, 3])  # Mudando a proporção das colunas, dando mais espaço para col2

with col1:
    # Gráfico de Tipo (rosca)
    st.markdown("### Distribution by Type")
    type_counts = df_filtered["type"].value_counts().reset_index()
    type_counts.columns = ["type", "count"]
    fig_pie = px.pie(type_counts, values="count", names="type", hole=0.5)
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    # Timeline - Gráfico de evolução temporal dos títulos
    st.markdown("### Titles Over Time")
    titles_by_year = df_filtered["release_year"].value_counts().sort_index().reset_index()
    titles_by_year.columns = ["release_year", "count"]
    fig_timeline = px.line(titles_by_year, x="release_year", y="count", markers=True)
    st.plotly_chart(fig_timeline, use_container_width=True)

# Gráfico "Top 10 Countries by Number of Titles" - Agora ocupa toda a largura
st.markdown("### Top 10 Countries by Number of Titles")
country_counts = df_filtered["country"].value_counts().nlargest(10).reset_index()
country_counts.columns = ["country", "count"]
fig_country = px.bar(country_counts, x="country", y="count", text="count")
st.plotly_chart(fig_country, use_container_width=True)

# Gráfico de Gênero (barras verticais)
st.markdown("### Top 10 Genres by Number of Titles")
genre_counts = df_filtered["listed_in"].value_counts().nlargest(10).reset_index()
genre_counts.columns = ["listed_in", "count"]
fig_genre = px.bar(genre_counts, x="listed_in", y="count", text="count")
st.plotly_chart(fig_genre, use_container_width=True)

# Tabela de dados
st.markdown("### Titles Table")
st.dataframe(df_filtered[["title", "type", "duration", "release_year"]])
