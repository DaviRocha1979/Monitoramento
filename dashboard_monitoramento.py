import streamlit as st
import pandas as pd

st.set_page_config(page_title="Painel de Monitoramento", layout="wide")

st.title("🔍 Painel de Monitoramento Internacional")

st.markdown("Fonte: [Planilha Google Sheets](https://docs.google.com/spreadsheets/d/1ljtZIWqQqfFYj6ubxpc8okHknoS1cuVXH0nq_lD6oOk/edit)")

# Leitura da planilha pública
sheet_url = "https://docs.google.com/spreadsheets/d/1ljtZIWqQqfFYj6ubxpc8okHknoS1cuVXH0nq_lD6oOk/export?format=csv"

try:
    df = pd.read_csv(sheet_url)
    st.subheader("📊 Dados da Planilha Google")
    st.dataframe(df)
except Exception as e:
    st.error("❌ Erro ao carregar a planilha. Verifique se o link está público ou se o formato está correto.")
    st.exception(e)
