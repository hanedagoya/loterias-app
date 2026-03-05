import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import itertools
from collections import Counter
from sklearn.ensemble import RandomForestClassifier
from scipy.stats import entropy
import random

st.set_page_config(page_title="Análise Científica de Loterias", layout="wide")

st.title("🔬 Plataforma Científica de Análise de Loterias")

uploaded_file = st.file_uploader(
    "Envie o arquivo oficial da Caixa (.xlsx)",
    type=["xlsx"]
)

if uploaded_file is None:
    st.info("Envie o arquivo para iniciar.")
    st.stop()

df = pd.read_excel(uploaded_file)

# detectar colunas de números
colunas = [c for c in df.columns if "bola" in c.lower() or "dezena" in c.lower()]
df = df[colunas]

numeros = df.values.flatten()

max_num = int(np.max(numeros))

st.sidebar.header("Configurações")

tipo = st.sidebar.selectbox(
    "Tipo de jogo",
    ["Mega-Sena", "Lotofácil"]
)

if tipo == "Mega-Sena":
    numeros_totais = 60
    numeros_jogo = 6
else:
    numeros_totais = 25
    numeros_jogo = 15

# ----------------------------
# Frequência
# ----------------------------

freq = Counter(numeros)

freq_df = pd.DataFrame({
    "numero": list(range(1, numeros_totais + 1)),
    "frequencia": [freq.get(i,0) for i in range(1,numeros_totais+1)]
})

st.subheader("Frequência histórica")

fig = px.bar(freq_df, x="numero", y="frequencia")
st.plotly_chart(fig, use_container_width=True)

# ----------------------------
# Entropia
# ----------------------------

prob = freq_df["frequencia"] / freq_df["frequencia"].sum()
ent = entropy(prob)

st.subheader("Entropia de Shannon")

st.write(f"Entropia do sistema: **{ent:.4f}**")

# ----------------------------
# Correlação
# ----------------------------

st.subheader("Correlação entre posições")

corr = df.corr()

fig = px.imshow(corr, text_auto=True)
st.plotly_chart(fig, use_container_width=True)

# ----------------------------
# Modelo de Machine Learning
# ----------------------------

st.subheader("Modelo preditivo (Random Forest)")

X = []
y = []

for i in range(len(df)-1):

    atual = df.iloc[i].values
    prox = df.iloc[i+1].values

    for n in range(1, numeros_totais+1):

        X.append([n in atual])
        y.append(int(n in prox))

X = np.array(X)
y = np.array(y)

model = RandomForestClassifier(n_estimators=200)
model.fit(X, y)

probabilidades = []

for n in range(1, numeros_totais+1):

    p = model.predict_proba([[False]])[0][1]
    probabilidades.append(p)

prob_df = pd.DataFrame({
    "numero": range(1,numeros_totais+1),
    "probabilidade": probabilidades
})

fig = px.bar(prob_df, x="numero", y="probabilidade")
st.plotly_chart(fig, use_container_width=True)

# ----------------------------
# Simulação Monte Carlo
# ----------------------------

st.subheader("Simulação Monte Carlo")

simulacoes = st.slider("Número de simulações", 1000, 100000, 10000)

resultados = []

numeros_lista = list(range(1,numeros_totais+1))

for _ in range(simulacoes):

    jogo = random.sample(numeros_lista, numeros_jogo)

    score = sum(freq[n] for n in jogo)

    resultados.append((jogo,score))

resultados.sort(key=lambda x: x[1], reverse=True)

top = resultados[:20]

st.write("Top jogos simulados")

for jogo,score in top:

    st.write(jogo)

# ----------------------------
# Gerador otimizado
# ----------------------------

st.subheader("Gerador Inteligente de Jogos")

qtde = st.slider("Quantidade de jogos", 1, 20, 5)

melhores = prob_df.sort_values("probabilidade", ascending=False)

pool = list(melhores["numero"].head(30))

jogos = []

for _ in range(qtde):

    jogo = sorted(random.sample(pool, numeros_jogo))
    jogos.append(jogo)

for j in jogos:

    st.success(" | ".join(f"{n:02d}" for n in j))

# ----------------------------
# Backtesting
# ----------------------------

st.subheader("Backtesting")

acertos = []

for i in range(len(df)-1):

    sorteio = set(df.iloc[i+1].values)

    jogo = set(random.sample(pool, numeros_jogo))

    acertos.append(len(sorteio & jogo))

media = np.mean(acertos)

st.write(f"Média de acertos simulada: **{media:.2f}**")

fig = px.histogram(acertos)
st.plotly_chart(fig, use_container_width=True)
