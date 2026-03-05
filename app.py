import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Loteria Analytics Pro V3", layout="wide")

st.title("🎰 Loteria Analytics Pro V3")

# -----------------------------
# CONFIGURAÇÃO
# -----------------------------

loteria = st.sidebar.selectbox(
    "Escolha a loteria",
    ["Lotofácil","Mega-Sena"]
)

if loteria == "Lotofácil":

    TOTAL_NUMEROS = 25
    NUM_SORTEADOS = 15

else:

    TOTAL_NUMEROS = 60
    NUM_SORTEADOS = 6


arquivo = st.sidebar.file_uploader(
    "Upload do histórico da Caixa",
    type=["xlsx"]
)

# -----------------------------
# FUNÇÕES
# -----------------------------

def detectar_colunas(df):

    cols = []

    for c in df.columns:

        if "bola" in c.lower() or "dezena" in c.lower():

            cols.append(c)

    if len(cols) == 0:

        cols = df.columns[-NUM_SORTEADOS:]

    return cols


def calcular_frequencia(df):

    freq = df.apply(pd.Series.value_counts).fillna(0).sum(axis=1)

    freq = freq.reindex(range(1,TOTAL_NUMEROS+1),fill_value=0)

    return freq


def calcular_atraso(df):

    atrasos = {}

    total = len(df)

    for n in range(1,TOTAL_NUMEROS+1):

        linhas = df[df.eq(n).any(axis=1)].index

        if len(linhas) == 0:

            atrasos[n] = total

        else:

            atrasos[n] = total - linhas.max()

    return pd.Series(atrasos)


def modelo_probabilidade(df):

    freq = calcular_frequencia(df)

    recente = df.tail(50)

    rec_freq = calcular_frequencia(recente)

    atraso = calcular_atraso(df)

    prob = (
        freq*0.5 +
        rec_freq*0.3 +
        atraso*0.2
    )

    prob = prob + 1

    prob = prob / prob.sum()

    return prob


def gerar_jogo(prob):

    jogo = np.random.choice(
        prob.index,
        size=NUM_SORTEADOS,
        replace=False,
        p=prob.values
    )

    return sorted(jogo)


def soma_media(df):

    return df.sum(axis=1).mean()


def score_jogo(jogo,freq,atraso,media):

    soma = sum(jogo)

    score = 0

    for n in jogo:

        score += freq[n]*0.6
        score += atraso[n]*0.4

    score -= abs(soma-media)*0.5

    pares = sum(n%2==0 for n in jogo)

    score -= abs(pares-(NUM_SORTEADOS/2))*3

    return score

# -----------------------------
# EXECUÇÃO
# -----------------------------

if arquivo:

    df_raw = pd.read_excel(arquivo)

    cols = detectar_colunas(df_raw)

    df = df_raw[cols].astype(int)

    freq = calcular_frequencia(df)

    atraso = calcular_atraso(df)

    prob = modelo_probabilidade(df)

    media_soma = soma_media(df)

    menu = st.sidebar.selectbox(
        "Menu",
        [
            "Dashboard",
            "Frequência",
            "Atrasos",
            "Probabilidade",
            "Gerador Inteligente",
            "Backtesting"
        ]
    )

    # ---------------------

    if menu == "Dashboard":

        col1,col2,col3 = st.columns(3)

        col1.metric("Concursos",len(df))
        col2.metric("Mais sorteado",freq.idxmax())
        col3.metric("Mais atrasado",atraso.idxmax())

        st.dataframe(df.tail())

    # ---------------------

    if menu == "Frequência":

        fig,ax = plt.subplots()

        ax.bar(freq.index,freq.values)

        st.pyplot(fig)

    # ---------------------

    if menu == "Atrasos":

        fig,ax = plt.subplots()

        ax.bar(atraso.index,atraso.values)

        st.pyplot(fig)

    # ---------------------

    if menu == "Probabilidade":

        fig,ax = plt.subplots()

        ax.bar(prob.index,prob.values)

        st.pyplot(fig)

        tabela = pd.DataFrame({
            "Número":prob.index,
            "Probabilidade":prob.values
        })

        st.dataframe(tabela.sort_values("Probabilidade",ascending=False))

    # ---------------------

    if menu == "Gerador Inteligente":

        qtd = st.number_input("Jogos",1,50,5)

        candidatos = []

        for i in range(3000):

            jogo = gerar_jogo(prob)

            s = score_jogo(
                jogo,
                freq,
                atraso,
                media_soma
            )

            candidatos.append((jogo,s))

        candidatos = sorted(
            candidatos,
            key=lambda x:x[1],
            reverse=True
        )

        st.subheader("Melhores jogos")

        for j,s in candidatos[:qtd]:

            st.success(
                " | ".join(f"{n:02d}" for n in j)
            )

    # ---------------------

    if menu == "Backtesting":

        resultados = []

        for i in range(100,len(df)):

            treino = df.iloc[:i]

            prob_bt = modelo_probabilidade(treino)

            jogo = gerar_jogo(prob_bt)

            real = set(df.iloc[i])

            acertos = len(set(jogo)&real)

            resultados.append(acertos)

        resultados = pd.Series(resultados)

        fig,ax = plt.subplots()

        ax.hist(resultados,bins=NUM_SORTEADOS)

        st.pyplot(fig)

        st.metric("Média de acertos",resultados.mean())

else:

    st.info("Envie o arquivo histórico da Caixa.")
