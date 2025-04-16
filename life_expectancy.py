import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Life Expectancy - World Health Organization", layout="wide")
st.title("Life Expectancy - World Health Organization")

@st.cache_data
def load_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTQjEmUymi_u7F0rCclj4iGxccirBd4rKeZA3Ky6EyGPbjkGpgTG__oFjSLhxLLbaaBZU1b0wBLAEmO/pub?output=csv"
    df = pd.read_csv(url)

    df.columns = df.columns.str.strip()
    df["FactValueNumeric"] = df["FactValueNumeric"].astype(str).str.replace(",", ".", regex=False)
    df["FactValueNumeric"] = pd.to_numeric(df["FactValueNumeric"], errors="coerce")
    df["DateModified"] = pd.to_datetime(df["DateModified"], errors="coerce")
    df = df[df["Gender"] != "Both sexes"]
    return df

df = load_data()

# --- Gráfico 1: Gender x FactValueNumeric ---
st.subheader("Gender")
gender_mean = df.groupby("Gender")["FactValueNumeric"].mean().reset_index()
fig1 = px.bar(
    gender_mean,
    x="FactValueNumeric",
    y="Gender",
    orientation="h",
    color_discrete_sequence=["#1f77b4"],
    text=gender_mean["FactValueNumeric"].round(1),
    labels={"FactValueNumeric": "Life Expectancy (avg)", "Gender": "Gender"},
)
fig1.update_traces(textposition="inside")
st.plotly_chart(fig1, use_container_width=True)

# --- Gráfico 2: Top 10 Location x FactValueNumeric ---
st.subheader("Country")
location_mean = df.groupby("Location")["FactValueNumeric"].mean().reset_index()
top10 = location_mean.sort_values(by="FactValueNumeric", ascending=False).head(10)
fig2 = px.bar(
    top10,
    x="FactValueNumeric",
    y="Location",
    orientation="h",
    color_discrete_sequence=["#1f77b4"],
    text=top10["FactValueNumeric"].round(1),
    labels={"FactValueNumeric": "Life Expectancy (avg)", "Location": "Country"},
)
fig2.update_layout(yaxis=dict(autorange="reversed"))
fig2.update_traces(textposition="inside")
st.plotly_chart(fig2, use_container_width=True)

# --- Gráfico 3: Timeline ---
st.subheader("Timeline")
timeline_df = df.groupby(["DateModified", "Gender"])["FactValueNumeric"].mean().reset_index()
fig3 = px.line(
    timeline_df,
    x="DateModified",
    y="FactValueNumeric",
    color="Gender",
    markers=True,
    labels={"FactValueNumeric": "Life Expectancy (avg)", "DateModified": "Date", "Gender": "Gender"},
)
st.plotly_chart(fig3, use_container_width=True)
