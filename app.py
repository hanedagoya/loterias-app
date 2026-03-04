import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import chisquare

st.set_page_config(page_title="Análise Oficial Loterias", layout="wide")

st.title("📊 Análise Oficial - Mega-Sena & Lotofácil")

# ==============================
# Escolha da Loteria
# ==============================

loteria = st.sidebar.selectbox(
    "Escolha a Loteria",
    ["Mega-Sena", "Lotofácil"]
)

if loteria == "Mega-Sena":
    total_numeros = 60
    dezenas = 6
else:
    total_numeros = 25
    dezenas = 15

# ==============================
# Upload do Arquivo Oficial
# ==============================

st.subheader("📂 Upload do arquivo oficial (.xlsx) da Caixa")

arquivo = st.file_uploader("Envie o arquivo .xlsx", type=["xlsx"])

if arquivo is not None:

    df_raw = pd.read_excel(arquivo)

    # Detectar automaticamente colunas de dezenas
    colunas_numericas = df_raw.select_dtypes(include=np.number).columns

    # Pegar últimas colunas numéricas (onde ficam as dezenas)
    df = df_raw[colunas_numericas].iloc[:, -dezenas:]

    st.success("Arquivo carregado com sucesso!")

    # ==============================
    # Estatísticas
    # ==============================

    valores = df.values.flatten()
    freq = pd.Series(valores).value_counts().sort_index()

    soma = df.sum(axis=1)
    pares = df.apply(lambda x: sum(n % 2 == 0 for n in x), axis=1)

    stat, p = chisquare(freq, [freq.sum()/total_numeros]*total_numeros)

    col1, col2, col3 = st.columns(3)

    col1.metric("Média da Soma", round(soma.mean(), 2))
    col2.metric("Média de Pares", round(pares.mean(), 2))
    col3.metric("p-value Qui²", round(p, 4))

    # ==============================
    # Frequência
    # ==============================

    st.subheader("Frequência Real dos Números")

    fig, ax = plt.subplots()
    ax.bar(freq.index, freq.values)
    st.pyplot(fig)

    # ==============================
    # Ranking
    # ==============================

    st.subheader("🔥 Top 10 Mais Frequentes")
    st.write(freq.sort_values(ascending=False).head(10))

    # ==============================
    # Gerador Baseado em Frequência
    # ==============================

    st.subheader("🎯 Gerar Jogo Baseado na Frequência")

    if st.button("Gerar Jogo Inteligente"):
        probabilidades = freq / freq.sum()
        jogo = np.random.choice(
            freq.index,
            size=dezenas,
            replace=False,
            p=probabilidades
        )

        jogo = sorted([int(n) for n in jogo])
        st.success(" | ".join(f"{n:02d}" for n in jogo))
