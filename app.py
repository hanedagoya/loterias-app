import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from scipy.stats import entropy
from sklearn.ensemble import RandomForestClassifier

st.set_page_config(page_title="Loteria Analytics V4", layout="wide")

st.title("🎰 Loteria Analytics V4")

# ----------------------------
# CONFIGURAÇÃO
# ----------------------------

loteria = st.sidebar.selectbox(
    "Loteria",
    ["Lotofácil","Mega-Sena"]
)

if loteria == "Lotofácil":

    TOTAL_NUMEROS = 25
    NUM_SORTEADOS = 15

else:

    TOTAL_NUMEROS = 60
    NUM_SORTEADOS = 6


arquivo = st.sidebar.file_uploader(
    "Upload arquivo histórico (.xlsx)",
    type=["xlsx"]
)

# ----------------------------
# FUNÇÕES
# ----------------------------

def detectar_colunas(df):

    cols=[]

    for c in df.columns:

        if "bola" in c.lower() or "dezena" in c.lower():

            cols.append(c)

    if len(cols)==0:

        cols=df.columns[-NUM_SORTEADOS:]

    return cols


def calcular_frequencia(df):

    freq=df.apply(pd.Series.value_counts).fillna(0).sum(axis=1)

    freq=freq.reindex(range(1,TOTAL_NUMEROS+1),fill_value=0)

    return freq


def calcular_atraso(df):

    atrasos={}

    total=len(df)

    for n in range(1,TOTAL_NUMEROS+1):

        linhas=df[df.eq(n).any(axis=1)].index

        if len(linhas)==0:

            atrasos[n]=total

        else:

            atrasos[n]=total-linhas.max()

    return pd.Series(atrasos)


def calcular_entropia(freq):

    prob=freq/freq.sum()

    ent=entropy(prob,base=2)

    return ent


def modelo_probabilidade(df):

    freq=calcular_frequencia(df)

    recente=df.tail(50)

    rec_freq=calcular_frequencia(recente)

    atraso=calcular_atraso(df)

    prob=(
        freq*0.5+
        rec_freq*0.3+
        atraso*0.2
    )

    prob=prob+1

    prob=prob/prob.sum()

    return prob


def gerar_jogo(prob):

    jogo=np.random.choice(
        prob.index,
        size=NUM_SORTEADOS,
        replace=False,
        p=prob.values
    )

    return sorted(jogo)


def soma_media(df):

    return df.sum(axis=1).mean()


def score_jogo(jogo,freq,atraso,media):

    soma=sum(jogo)

    score=0

    for n in jogo:

        score+=freq[n]*0.6
        score+=atraso[n]*0.4

    score-=abs(soma-media)*0.5

    pares=sum(n%2==0 for n in jogo)

    score-=abs(pares-(NUM_SORTEADOS/2))*2

    return score


def criar_dataset(df):

    X=[]
    y=[]

    for i in range(20,len(df)):

        janela=df.iloc[i-20:i]

        freq=calcular_frequencia(janela)

        X.append(freq.values)

        atual=set(df.iloc[i])

        linha=[1 if n in atual else 0 for n in range(1,TOTAL_NUMEROS+1)]

        y.append(linha)

    return np.array(X),np.array(y)


# ----------------------------
# EXECUÇÃO
# ----------------------------

if arquivo:

    df_raw=pd.read_excel(arquivo)

    cols=detectar_colunas(df_raw)

    df=df_raw[cols].astype(int)

    freq=calcular_frequencia(df)

    atraso=calcular_atraso(df)

    prob=modelo_probabilidade(df)

    media_soma=soma_media(df)

    ent=calcular_entropia(freq)

    ent_max=np.log2(TOTAL_NUMEROS)

    indice=ent/ent_max

    menu=st.sidebar.selectbox(
        "Menu",
        [
            "Dashboard",
            "Frequência",
            "Atrasos",
            "Entropia",
            "Par / Ímpar",
            "Soma",
            "Probabilidade",
            "Machine Learning",
            "Gerador Inteligente",
            "Backtesting"
        ]
    )

# ----------------------------
# DASHBOARD
# ----------------------------

    if menu=="Dashboard":

        col1,col2,col3,col4=st.columns(4)

        col1.metric("Concursos",len(df))
        col2.metric("Mais sorteado",freq.idxmax())
        col3.metric("Mais atrasado",atraso.idxmax())
        col4.metric("Entropia",round(ent,3))

        st.dataframe(df.tail())

# ----------------------------
# FREQUÊNCIA
# ----------------------------

    if menu=="Frequência":

        fig,ax=plt.subplots()

        ax.bar(freq.index,freq.values)

        st.pyplot(fig)

        tabela=pd.DataFrame({
            "Número":freq.index,
            "Frequência":freq.values
        })

        st.dataframe(tabela.sort_values("Frequência",ascending=False))

# ----------------------------
# ATRASOS
# ----------------------------

    if menu=="Atrasos":

        fig,ax=plt.subplots()

        ax.bar(atraso.index,atraso.values)

        st.pyplot(fig)

        tabela=pd.DataFrame({
            "Número":atraso.index,
            "Atraso":atraso.values
        })

        st.dataframe(tabela.sort_values("Atraso",ascending=False))

# ----------------------------
# ENTROPIA
# ----------------------------

    if menu=="Entropia":

        st.metric("Entropia observada",round(ent,3))

        st.metric("Entropia máxima",round(ent_max,3))

        st.metric("Índice de aleatoriedade",round(indice,3))

        st.write("""
Interpretação aproximada:

> 0.98 → extremamente aleatório  
0.95–0.98 → quase aleatório  
<0.95 → possível padrão
""")

# ----------------------------
# PAR / ÍMPAR
# ----------------------------

    if menu=="Par / Ímpar":

        pares=df.apply(lambda x:sum(n%2==0 for n in x),axis=1)

        dist=pares.value_counts().sort_index()

        fig,ax=plt.subplots()

        ax.bar(dist.index,dist.values)

        st.pyplot(fig)

        st.dataframe(dist)

# ----------------------------
# SOMA
# ----------------------------

    if menu=="Soma":

        soma=df.sum(axis=1)

        fig,ax=plt.subplots()

        ax.hist(soma,bins=20)

        st.pyplot(fig)

        st.metric("Soma média",round(soma.mean(),2))

# ----------------------------
# PROBABILIDADE
# ----------------------------

    if menu=="Probabilidade":

        tabela=pd.DataFrame({
            "Número":prob.index,
            "Probabilidade":prob.values
        })

        st.dataframe(tabela.sort_values("Probabilidade",ascending=False))

        fig,ax=plt.subplots()

        ax.bar(prob.index,prob.values)

        st.pyplot(fig)

# ----------------------------
# MACHINE LEARNING
# ----------------------------

    if menu=="Machine Learning":

        st.write("Treinando modelo...")

        X,y=criar_dataset(df)

        model=RandomForestClassifier()

        model.fit(X,y)

        ultima=df.tail(20)

        freq_ultima=calcular_frequencia(ultima)

        pred=model.predict_proba([freq_ultima.values])

        probs=[p[1] for p in pred]

        tabela=pd.DataFrame({
            "Número":range(1,TOTAL_NUMEROS+1),
            "Probabilidade ML":probs
        })

        st.dataframe(tabela.sort_values("Probabilidade ML",ascending=False))

# ----------------------------
# GERADOR
# ----------------------------

    if menu=="Gerador Inteligente":

        qtd=st.number_input("Jogos",1,20,5)

        candidatos=[]

        for i in range(5000):

            jogo=gerar_jogo(prob)

            s=score_jogo(jogo,freq,atraso,media_soma)

            candidatos.append((jogo,s))

        candidatos=sorted(
            candidatos,
            key=lambda x:x[1],
            reverse=True
        )

        for j,s in candidatos[:qtd]:

            st.success(" | ".join(f"{n:02d}" for n in j))

# ----------------------------
# BACKTEST
# ----------------------------

    if menu=="Backtesting":

        resultados=[]

        for i in range(100,len(df)):

            treino=df.iloc[:i]

            prob_bt=modelo_probabilidade(treino)

            jogo=gerar_jogo(prob_bt)

            real=set(df.iloc[i])

            acertos=len(set(jogo)&real)

            resultados.append(acertos)

        resultados=pd.Series(resultados)

        fig,ax=plt.subplots()

        ax.hist(resultados,bins=NUM_SORTEADOS)

        st.pyplot(fig)

        st.metric("Média de acertos",round(resultados.mean(),2))

else:

    st.info("Envie o arquivo histórico da Caixa.")
