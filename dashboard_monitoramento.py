import streamlit as st

st.set_page_config(page_title="Painel de Monitoramento", layout="wide")

st.title("🔍 Painel de Monitoramento Internacional")

query = st.text_input("Digite sua palavra-chave:", "cooperação internacional")

if st.button("Buscar"):
    st.info(f"Buscando por: '{query}' (exemplo de simulação)")
    st.write("📄 Resultados simulados (neste exemplo):")
    st.write([
        {"título": "Cooperação cresce na CPLP", "data": "2025-04-25"},
        {"título": "Nova parceria internacional firmada", "data": "2025-04-26"}
    ])
