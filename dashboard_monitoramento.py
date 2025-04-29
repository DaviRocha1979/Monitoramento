
import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from langdetect import detect
from datetime import datetime

# URL da planilha
URL = "https://docs.google.com/spreadsheets/d/1ljtZIWqQqfFYj6ubxpc8okHknoS1cuVXH0nq_lD6oOk/export?format=csv"

st.title("🌍 Painel de Monitoramento Internacional")
st.write("Este painel coleta links de fontes oficiais e faz leitura de conteúdo relevante por país, fonte e tema.")

# Carrega a planilha
df_raw = pd.read_csv(URL)

# Transforma a planilha: linhas = fontes, colunas = países
df_long = df_raw.set_index(df_raw.columns[0]).T
df_long = df_long.reset_index().rename(columns={"index": "País"})

# Sidebar de filtros
paises = df_long["País"].unique().tolist()
pais = st.sidebar.selectbox("🌐 Selecione o país", paises)

tipos = df_raw[df_raw.columns[0]].tolist()
tipo = st.sidebar.selectbox("🏛️ Tipo de fonte", tipos)

tema = st.sidebar.text_input("📰 Tema a buscar nas notícias", "vacinação")

# Filtra os links com base nos critérios
links = df_long[df_long["País"] == pais][tipo].dropna().tolist()

st.subheader(f"🔗 {len(links)} links encontrados para análise")

# Função para extrair texto do link
def extrair_conteudo(url):
    try:
        resposta = requests.get(url, timeout=5)
        sopa = BeautifulSoup(resposta.content, "html.parser")
        paragrafos = [p.get_text() for p in sopa.find_all("p")]
        conteudo = " ".join(paragrafos)
        idioma = detect(conteudo)
        return conteudo, idioma
    except:
        return "", "erro"

# Coleta resultados relevantes
resultados = []
for url in links:
    texto, idioma = extrair_conteudo(url)
    if tema.lower() in texto.lower() and idioma == "pt":
        resultados.append({
            "URL": url,
            "Idioma": idioma,
            "Data de Coleta": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "Trecho Encontrado": texto[:300] + "..." if len(texto) > 300 else texto
        })

# Exibe resultados
if resultados:
    st.success(f"{len(resultados)} resultados encontrados com o tema '{tema}' em português:")
    for r in resultados:
        st.markdown(f"### 🔗 [{r['URL']}]({r['URL']})")
        st.markdown(f"📅 Coleta: {r['Data de Coleta']} | 🌐 Idioma: {r['Idioma']}")
        st.write(r["Trecho Encontrado"])
        st.markdown("---")
else:
    st.warning("Nenhuma notícia encontrada com o tema e idioma especificado.")
