import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import chisquare

st.set_page_config(page_title="Análise Loterias", layout="wide")

st.title("📊 Análise Estatística - Mega-Sena & Lotofácil")

# ------------------------------
# Escolha da loteria
# ------------------------------

loteria = st.sidebar.selectbox(
    "Escolha a loteria",
    ["Mega-Sena", "Lotofácil"]
)

if loteria == "Mega-Sena":
    total_numeros = 60
    dezenas = 6
else:
    total_numeros = 25
    dezenas = 15

# ------------------------------
# Upload do arquivo
# ------------------------------

st.subheader("📂 Upload do arquivo oficial (.xlsx)")

arquivo = st.file_uploader(
    "Envie o arquivo baixado do site da Caixa",
    type=["xlsx"]
)

if arquivo is not None:

    df_raw = pd.read_excel(arquivo)

    # pegar apenas colunas numéricas
    colunas_numericas = df_raw.select_dtypes(include=np.number)

    # pegar últimas colunas (onde ficam as dezenas)
    df = colunas_numericas.iloc[:, -dezenas:]

    st.success("Arquivo carregado com sucesso!")

    # ------------------------------
    # Estatísticas
    # ------------------------------

    valores = df.values.flatten()

    freq = pd.Series(valores).value_counts().sort_index()
    freq = freq.reindex(range(1, total_numeros + 1), fill_value=0)

    soma = df.sum(axis=1)

    pares = df.apply(lambda x: sum(n % 2 == 0 for n in x), axis=1)

    stat, p = chisquare(freq, [freq.sum() / total_numeros] * total_numeros)

    col1, col2, col3 = st.columns(3)

    col1.metric("Média da soma", round(soma.mean(), 2))
    col2.metric("Média de pares", round(pares.mean(), 2))
    col3.metric("p-value Qui²", round(p, 4))

    # ------------------------------
    # Gráfico frequência
    # ------------------------------

    st.subheader("Frequência dos números")

    fig, ax = plt.subplots()
    ax.bar(freq.index, freq.values)

    st.pyplot(fig)

    # ------------------------------
    # Top números
    # ------------------------------

    st.subheader("🔥 Top 10 mais frequentes")

    st.write(freq.sort_values(ascending=False).head(10))

    # ------------------------------
    # Gerador de jogo
    # ------------------------------

    st.subheader("🎲 Gerar jogo baseado na frequência")

    if st.button("Gerar jogo"):

        probabilidades = freq / freq.sum()

        jogo = np.random.choice(
            freq.index,
            size=dezenas,
            replace=False,
            p=probabilidades
        )

        jogo = sorted([int(n) for n in jogo])

        jogo_formatado = " | ".join(f"{n:02d}" for n in jogo)

        st.success(jogo_formatado)
