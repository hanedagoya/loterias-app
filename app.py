import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import random
from collections import Counter
from scipy.stats import entropy

st.set_page_config(page_title="Laboratório Estatístico de Loterias", layout="wide")

st.title("🧠 Laboratório Estatístico de Loterias")

st.markdown("""
Ferramenta para análise estatística de loterias brasileiras.

Funciona com arquivos oficiais da Caixa (.xlsx).

Inclui:

• Frequência histórica
• Ranking de números
• Entropia do sistema
• Atraso das dezenas
• Co-ocorrência entre números
• Simulação Monte Carlo
• Gerador estatístico
• Backtesting
""")

uploaded_file = st.file_uploader("Envie o arquivo .xlsx da Caixa", type=["xlsx"])

if uploaded_file is None:
st.info("Envie o arquivo para iniciar a análise.")
st.stop()

# -----------------------------

# LEITURA DO EXCEL

# -----------------------------

try:
df_raw = pd.read_excel(uploaded_file)
except Exception:
st.error("Erro ao ler o arquivo Excel.")
st.stop()

# detectar colunas de dezenas

cols = []

for c in df_raw.columns:

```
name = str(c).lower()

if "bola" in name or "dezena" in name:
    cols.append(c)
```

if len(cols) == 0:

```
st.error("Não foi possível identificar as colunas de dezenas.")

st.stop()
```

df = df_raw[cols].copy()

df = df.apply(pd.to_numeric, errors="coerce")

df = df.dropna()

if len(df) == 0:

```
st.error("Dataset vazio após limpeza.")

st.stop()
```

numeros = df.values.flatten().astype(int)

# -----------------------------

# CONFIGURAÇÃO DO JOGO

# -----------------------------

st.sidebar.header("Configuração")

tipo = st.sidebar.selectbox("Tipo de jogo", ["Mega-Sena", "Lotofácil"])

if tipo == "Mega-Sena":
total_numeros = 60
numeros_jogo = 6
else:
total_numeros = 25
numeros_jogo = 15

todos = list(range(1, total_numeros + 1))

# -----------------------------

# FREQUÊNCIA

# -----------------------------

st.header("📊 Frequência Histórica")

freq = Counter(numeros)

freq_df = pd.DataFrame({
"numero": todos,
"freq": [freq.get(i,0) for i in todos]
})

fig = px.bar(freq_df, x="numero", y="freq")

st.plotly_chart(fig, use_container_width=True)

# ranking

ranking = freq_df.sort_values("freq", ascending=False)

st.subheader("Ranking de dezenas")

st.dataframe(ranking)

# -----------------------------

# ENTROPIA

# -----------------------------

st.header("🧮 Entropia de Shannon")

prob = freq_df["freq"] / freq_df["freq"].sum()

ent = entropy(prob)

st.metric("Entropia", round(ent,4))

# -----------------------------

# ATRASO DAS DEZENAS

# -----------------------------

st.header("⏳ Atraso das dezenas")

delay = {}

for n in todos:

```
atraso = 0

for i in range(len(df)-1,-1,-1):

    if n in df.iloc[i].values:
        atraso = len(df) - i
        break

delay[n] = atraso
```

delay_df = pd.DataFrame({
"numero": list(delay.keys()),
"atraso": list(delay.values())
})

fig = px.bar(delay_df, x="numero", y="atraso")

st.plotly_chart(fig, use_container_width=True)

# -----------------------------

# SOMA DOS JOGOS

# -----------------------------

st.header("➕ Distribuição da soma")

soma = df.sum(axis=1)

fig = px.histogram(soma)

st.plotly_chart(fig, use_container_width=True)

st.metric("Média da soma", round(soma.mean(),2))

# -----------------------------

# PAR / ÍMPAR

# -----------------------------

st.header("⚖ Par vs Ímpar")

pares = df.apply(lambda x: sum(n%2==0 for n in x), axis=1)

fig = px.histogram(pares)

st.plotly_chart(fig, use_container_width=True)

st.metric("Média de pares", round(pares.mean(),2))

# -----------------------------

# COOCORRÊNCIA

# -----------------------------

st.header("🔥 Co-ocorrência entre dezenas")

matrix = np.zeros((total_numeros,total_numeros))

for row in df.values:

```
for a in row:
    for b in row:

        if a!=b:
            matrix[a-1][b-1]+=1
```

fig = px.imshow(matrix)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------

# MONTE CARLO

# -----------------------------

st.header("🎲 Simulação Monte Carlo")

sim = st.slider("Número de simulações",1000,20000,5000)

results = []

for _ in range(sim):

```
jogo = random.sample(todos,numeros_jogo)

score = sum(freq.get(n,0) for n in jogo)

results.append((jogo,score))
```

results.sort(key=lambda x:x,reverse=True)

top = results[:10]

st.subheader("Top jogos simulados")

for j,s in top:

```
st.write(sorted(j))
```

# -----------------------------

# GERADOR EQUILIBRADO

# -----------------------------

st.header("🎯 Gerador equilibrado")

if st.button("Gerar jogo equilibrado"):

```
while True:

    jogo = random.sample(todos,numeros_jogo)

    pares = sum(n%2==0 for n in jogo)

    soma = sum(jogo)

    if tipo=="Mega-Sena":

        if 2<=pares<=4 and 120<soma<220:
            break

    else:

        if 6<=pares<=9 and 150<soma<220:
            break

st.success(" | ".join(f"{n:02d}" for n in sorted(jogo)))
```

# -----------------------------

# BACKTESTING

# -----------------------------

st.header("🧪 Backtesting")

pool = ranking.head(30)["numero"].tolist()

hits = []

for i in range(len(df)-1):

```
real = set(df.iloc[i+1].values)

jogo = set(random.sample(pool,numeros_jogo))

hits.append(len(real & jogo))
```

media = np.mean(hits)

st.metric("Média de acertos simulada", round(media,2))

fig = px.histogram(hits)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

st.caption("Loterias são processos aleatórios independentes. Esta ferramenta é apenas para estudo estatístico.")
