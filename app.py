import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations
from collections import Counter

st.set_page_config(page_title="Análise de Loterias", layout="wide")

st.title("📊 Ferramenta Estatística de Análise de Loterias")

st.sidebar.title("Configurações")

uploaded_file = st.sidebar.file_uploader(
    "Upload arquivo oficial da Caixa (.xlsx)",
    type=["xlsx"]
)

if uploaded_file:

    df_raw = pd.read_excel(uploaded_file)

    st.success("Arquivo carregado com sucesso!")

    # detectar colunas de números
    cols_numeros = [c for c in df_raw.columns if "Bola" in c or "bola" in c or "Dezena" in c]

    if len(cols_numeros) == 0:
        cols_numeros = df_raw.columns[-15:]

    df = df_raw[cols_numeros].copy()

    df = df.astype(int)

    total_concursos = len(df)

    st.sidebar.write("Concursos carregados:", total_concursos)

    numeros = list(range(1, 26))

    menu = st.sidebar.selectbox(
        "Menu",
        [
            "Visão geral",
            "Frequência dos números",
            "Números atrasados",
            "Par / Ímpar",
            "Soma dos jogos",
            "Repetição entre concursos",
            "Combinações mais comuns",
            "Gerador inteligente"
        ]
    )

    if menu == "Visão geral":

        st.header("Resumo do histórico")

        st.write("Total de concursos analisados:", total_concursos)

        st.dataframe(df.tail())

    if menu == "Frequência dos números":

        st.header("Frequência dos números")

        freq = df.apply(pd.Series.value_counts).fillna(0).sum(axis=1)

        freq = freq.sort_index()

        fig, ax = plt.subplots()

        ax.bar(freq.index, freq.values)

        ax.set_xlabel("Número")
        ax.set_ylabel("Frequência")

        st.pyplot(fig)

        st.subheader("Ranking")

        ranking = freq.sort_values(ascending=False)

        st.dataframe(ranking)

    if menu == "Números atrasados":

        st.header("Atraso dos números")

        atrasos = {}

        for n in numeros:

            linhas = df[df.eq(n).any(axis=1)].index

            if len(linhas) == 0:

                atrasos[n] = total_concursos

            else:

                atrasos[n] = total_concursos - linhas.max()

        atrasos = pd.Series(atrasos)

        fig, ax = plt.subplots()

        ax.bar(atrasos.index, atrasos.values)

        ax.set_xlabel("Número")
        ax.set_ylabel("Concursos de atraso")

        st.pyplot(fig)

        st.dataframe(atrasos.sort_values(ascending=False))

    if menu == "Par / Ímpar":

        st.header("Distribuição Par / Ímpar")

        pares = df.apply(lambda x: sum(n % 2 == 0 for n in x), axis=1)

        impares = 15 - pares

        dist = pares.value_counts().sort_index()

        fig, ax = plt.subplots()

        ax.bar(dist.index, dist.values)

        ax.set_xlabel("Quantidade de pares no jogo")
        ax.set_ylabel("Ocorrências")

        st.pyplot(fig)

        tabela = pd.DataFrame({
            "pares": pares,
            "ímpares": impares
        })

        st.dataframe(tabela)

    if menu == "Soma dos jogos":

        st.header("Distribuição da soma")

        soma = df.sum(axis=1)

        fig, ax = plt.subplots()

        ax.hist(soma, bins=20)

        ax.set_xlabel("Soma dos números")

        st.pyplot(fig)

        st.write("Soma média:", soma.mean())

    if menu == "Repetição entre concursos":

        st.header("Repetição de números entre concursos")

        repeticoes = []

        for i in range(1, total_concursos):

            atual = set(df.iloc[i])

            anterior = set(df.iloc[i-1])

            repeticoes.append(len(atual & anterior))

        repeticoes = pd.Series(repeticoes)

        fig, ax = plt.subplots()

        ax.hist(repeticoes, bins=10)

        ax.set_xlabel("Quantidade de números repetidos")

        st.pyplot(fig)

        st.write("Média de repetição:", repeticoes.mean())

    if menu == "Combinações mais comuns":

        st.header("Pares mais frequentes")

        pares = Counter()

        for row in df.values:

            for c in combinations(row, 2):

                pares[c] += 1

        mais_comuns = pares.most_common(20)

        tabela = pd.DataFrame(mais_comuns, columns=["Par", "Frequência"])

        st.dataframe(tabela)

    if menu == "Gerador inteligente":

        st.header("Gerador inteligente de jogos")

        qtd = st.number_input(
            "Quantidade de jogos",
            min_value=1,
            max_value=50,
            value=5
        )

        freq = df.apply(pd.Series.value_counts).fillna(0).sum(axis=1)

        prob = freq / freq.sum()

        jogos = []

        for i in range(qtd):

            jogo = np.random.choice(
                prob.index,
                size=15,
                replace=False,
                p=prob.values
            )

            jogo = sorted(jogo)

            jogos.append(jogo)

        st.subheader("Jogos gerados")

        for j in jogos:

            st.success(" | ".join(f"{n:02d}" for n in j))

else:

    st.info("Faça upload do arquivo histórico da Caixa para iniciar.")
