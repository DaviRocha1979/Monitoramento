import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from langdetect import detect
from datetime import datetime
import feedparser
import re

# URL da planilha CSV pública
URL_SHEET = "https://docs.google.com/spreadsheets/d/1ljtZIWqQqfFYj6ubxpc8okHknoS1cuVXH0nq_lD6oOk/export?format=csv"

st.set_page_config(page_title="Painel Monitoramento Automático", layout="wide")
st.title("🌐 Painel de Notícias – Autodetecção de RSS / Crawler")

# Carrega planilha
df = pd.read_csv(URL_SHEET)
col_fonte = df.columns[0]
df_long = df.set_index(col_fonte).T.reset_index().rename(columns={"index":"País"})

# Filtros
paises = df_long["País"].unique().tolist()
pais = st.sidebar.selectbox("País", paises)
tipos = ["(todas)"] + df[col_fonte].tolist()
tipo = st.sidebar.selectbox("Tipo de fonte", tipos)
tema = st.sidebar.text_input("Tema (opcional)", "").strip().lower()

# Seleciona URLs
sub = df_long[df_long["País"]==pais]
if tipo=="(todas)":
    urls = sub.drop("País", axis=1).values.flatten().tolist()
else:
    urls = sub[tipo].dropna().tolist()
urls = [u for u in urls if isinstance(u,str) and u.startswith("http")]

st.subheader(f"🔗 {len(urls)} fontes encontradas em {pais}")

# Função de autodetecção de RSS
def encontra_feed(url):
    try:
        r = requests.get(url, timeout=5)
        soup = BeautifulSoup(r.content, "html.parser")
        # procura <link rel="alternate" type="application/rss+xml">
        tag = soup.find("link", {"type":"application/rss+xml"})
        if tag and tag.get("href"):
            return requests.compat.urljoin(url, tag["href"])
        # tenta padrões comuns
        for suf in ["/feed", "/rss", "/rss.xml", "/feeds/posts/default"]:
            tentativa = url.rstrip("/") + suf
            if requests.head(tentativa, timeout=3).status_code == 200:
                return tentativa
    except:
        pass
    return None

# Função que coleta últimas notícias de um feed ou crawler
def coleta_noticias(url, max_itens=5):
    feed = encontra_feed(url)
    itens = []
    if feed:
        d = feedparser.parse(feed)
        for entry in d.entries[:max_itens]:
            link = entry.link
            title = entry.title
            date = entry.get("published", entry.get("updated", ""))
            itens.append((title, link, date))
    else:
        # crawler leve: busca links de artigos com padrão de data
        try:
            r = requests.get(url, timeout=5)
            soup = BeautifulSoup(r.content, "html.parser")
            # todos <a> com /YYYY/MM/DD/ ou /YYYY-MM-DD/
            candidates = set()
            for a in soup.find_all("a", href=True):
                if re.search(r"/20\d{2}[-/]\d{2}[-/]\d{2}", a["href"]):
                    candidates.add(requests.compat.urljoin(url, a["href"]))
            for link in list(candidates)[:max_itens]:
                # extrai texto para exibir título
                txt = requests.get(link, timeout=5).text
                soup2 = BeautifulSoup(txt, "html.parser")
                h = soup2.find(["h1","h2"])
                title = h.get_text().strip() if h else link
                date = ""
                itens.append((title, link, date))
        except:
            pass
    return itens

# Processo de coleta e filtro
resultados = []
for u in urls:
    for title, link, date in coleta_noticias(u, max_itens=3):
        # extrai conteúdo para detectar idioma e tema
        try:
            txt = requests.get(link, timeout=5).text
            soup = BeautifulSoup(txt, "html.parser")
            conteudo = " ".join(p.get_text() for p in soup.find_all("p"))
            idioma = detect(conteudo) if len(conteudo)>100 else "?"
        except:
            idioma = "?"
        if idioma.startswith("pt") and (tema=="" or tema in conteudo.lower()):
            resultados.append({
                "Fonte": u,
                "Título": title,
                "Link": link,
                "Data Publicação": date,
                "Idioma": idioma,
                "Coleta": datetime.now().strftime("%d/%m/%Y %H:%M")
            })

# Exibe tabela final
if resultados:
    df_res = pd.DataFrame(resultados)
    st.dataframe(df_res.drop_duplicates(subset=["Link"]),  height=500)
else:
    st.warning("Nenhuma notícia encontrada com esses filtros.")
