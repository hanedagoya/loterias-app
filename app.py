import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations
from collections import Counter

st.set_page_config(page_title="Loteria Analytics Pro", layout="wide")

st.title("🎰 Loteria Analytics Pro")

st.sidebar.title("Configurações")

arquivo = st.sidebar.file_uploader(
    "Upload histórico da Caixa (.xlsx)",
    type=["xlsx"]
)

# -----------------------------------
# Funções
# -----------------------------------

def detectar_colunas(df):

    cols = [c for c in df.columns if "bola" in c.lower() or "dezena" in c.lower()]

    if len(cols) == 0:
        cols = df.columns[-15:]

    return cols


def calcular_frequencia(df):

    freq = df.apply(pd.Series.value_counts).fillna(0).sum(axis=1)
    return freq.sort_index()


def calcular_atraso(df, numeros):

    atrasos = {}

    total = len(df)

    for n in numeros:

        linhas = df[df.eq(n).any(axis=1)].index

        if len(linhas) == 0:
            atrasos[n] = total
        else:
            atrasos[n] = total - linhas.max()

    return pd.Series(atrasos)


def modelo_probabilidade(df):

    freq = calcular_frequencia(df)

    recencia = df.tail(50)

    rec_freq = calcular_frequencia(recencia)

    prob = (freq * 0.7 + rec_freq * 0.3)

    prob = prob / prob.sum()

    return prob


def gerar_jogo(prob):

    jogo = np.random.choice(
        prob.index,
        size=15,
        replace=False,
        p=prob.values
    )

    return sorted(jogo)


def score_jogo(jogo, freq, atraso):

    s = 0

    for n in jogo:

        s += freq[n] * 0.7
        s += atraso[n] * 0.3

    return s


# -----------------------------------
# Interface
# -----------------------------------

if arquivo:

    df_raw = pd.read_excel(arquivo)

    cols = detectar_colunas(df_raw)

    df = df_raw[cols].astype(int)

    numeros = list(range(1, 26))

    freq = calcular_frequencia(df)

    atraso = calcular_atraso(df, numeros)

    prob = modelo_probabilidade(df)

    menu = st.sidebar.selectbox(
        "Menu",
        [
            "Dashboard",
            "Frequência",
            "Atrasos",
            "Heatmap",
            "Par / Ímpar",
            "Soma",
            "Repetições",
            "Combinações",
            "Probabilidade",
            "Gerador Inteligente",
            "Backtesting"
        ]
    )

    # -----------------------------------
    # Dashboard
    # -----------------------------------

    if menu == "Dashboard":

        col1, col2, col3 = st.columns(3)

        col1.metric("Concursos", len(df))
        col2.metric("Número mais sorteado", freq.idxmax())
        col3.metric("Número mais atrasado", atraso.idxmax())

        st.subheader("Últimos concursos")

        st.dataframe(df.tail())

    # -----------------------------------
    # Frequência
    # -----------------------------------

    if menu == "Frequência":

        st.header("Frequência dos números")

        fig, ax = plt.subplots()

        ax.bar(freq.index, freq.values)

        ax.set_xlabel("Número")
        ax.set_ylabel("Frequência")

        st.pyplot(fig)

        st.dataframe(freq.sort_values(ascending=False))

    # -----------------------------------
    # Atrasos
    # -----------------------------------

    if menu == "Atrasos":

        st.header("Números atrasados")

        fig, ax = plt.subplots()

        ax.bar(atraso.index, atraso.values)

        st.pyplot(fig)

        st.dataframe(atraso.sort_values(ascending=False))

    # -----------------------------------
    # Heatmap Lotofácil
    # -----------------------------------

    if menu == "Heatmap":

        st.header("Heatmap da Lotofácil")

        grid = np.zeros((5,5))

        for n in range(1,26):

            r = (n-1)//5
            c = (n-1)%5

            grid[r][c] = freq[n]

        fig, ax = plt.subplots()

        im = ax.imshow(grid)

        for i in range(5):
            for j in range(5):
                num = i*5 + j + 1
                ax.text(j, i, num, ha="center", va="center", color="white")

        st.pyplot(fig)

    # -----------------------------------
    # Par / Ímpar
    # -----------------------------------

    if menu == "Par / Ímpar":

        pares = df.apply(lambda x: sum(n%2==0 for n in x), axis=1)

        dist = pares.value_counts().sort_index()

        fig, ax = plt.subplots()

        ax.bar(dist.index, dist.values)

        st.pyplot(fig)

        st.write("Distribuição:")

        st.dataframe(dist)

    # -----------------------------------
    # Soma
    # -----------------------------------

    if menu == "Soma":

        soma = df.sum(axis=1)

        fig, ax = plt.subplots()

        ax.hist(soma, bins=20)

        st.pyplot(fig)

        st.write("Soma média:", soma.mean())

    # -----------------------------------
    # Repetições
    # -----------------------------------

    if menu == "Repetições":

        rep = []

        for i in range(1, len(df)):

            atual = set(df.iloc[i])
            anterior = set(df.iloc[i-1])

            rep.append(len(atual & anterior))

        rep = pd.Series(rep)

        fig, ax = plt.subplots()

        ax.hist(rep, bins=10)

        st.pyplot(fig)

        st.write("Média:", rep.mean())

    # -----------------------------------
    # Combinações
    # -----------------------------------

    if menu == "Combinações":

        pares = Counter()

        for row in df.values:

            for c in combinations(row,2):

                pares[c]+=1

        tabela = pd.DataFrame(
            pares.most_common(20),
            columns=["Par","Frequência"]
        )

        st.dataframe(tabela)

    # -----------------------------------
    # Probabilidade
    # -----------------------------------

    if menu == "Probabilidade":

        st.header("Probabilidade estimada")

        tabela = pd.DataFrame({
            "Número": prob.index,
            "Probabilidade": prob.values
        })

        st.dataframe(tabela.sort_values("Probabilidade",ascending=False))

        fig, ax = plt.subplots()

        ax.bar(prob.index, prob.values)

        st.pyplot(fig)

    # -----------------------------------
    # Gerador inteligente
    # -----------------------------------

    if menu == "Gerador Inteligente":

        st.header("Gerador otimizado")

        qtd = st.number_input("Jogos",1,100,5)

        jogos = []

        for i in range(qtd*10):

            jogo = gerar_jogo(prob)

            s = score_jogo(jogo,freq,atraso)

            jogos.append((jogo,s))

        jogos = sorted(jogos,key=lambda x:x[1],reverse=True)

        st.subheader("Melhores jogos")

        for j,s in jogos[:qtd]:

            st.success(" | ".join(f"{n:02d}" for n in j))

    # -----------------------------------
    # Backtesting
    # -----------------------------------

    if menu == "Backtesting":

        st.header("Simulação histórica")

        acertos = []

        for i in range(100,len(df)):

            treino = df.iloc[:i]

            prob = modelo_probabilidade(treino)

            jogo = gerar_jogo(prob)

            real = set(df.iloc[i])

            acerto = len(set(jogo) & real)

            acertos.append(acerto)

        acertos = pd.Series(acertos)

        fig, ax = plt.subplots()

        ax.hist(acertos,bins=10)

        st.pyplot(fig)

        st.write("Média de acertos:", acertos.mean())

else:

    st.info("Faça upload do arquivo histórico da Caixa.")
