import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import random
from collections import Counter
from scipy.stats import entropy
from sklearn.ensemble import RandomForestClassifier

st.set_page_config(page_title="Laboratório Científico de Loterias", layout="wide")

st.title("🧠 Laboratório Científico de Análise de Loterias")

st.markdown("""
Ferramenta experimental para estudo estatístico de loterias.

Inclui:

* Frequência histórica
* Entropia de Shannon
* Atraso de dezenas
* Matriz de co-ocorrência
* Probabilidade com Machine Learning
* Simulação Monte Carlo
* Gerador evolutivo de jogos
* Backtesting histórico
  """)

uploaded_file = st.file_uploader(
"Envie o arquivo oficial da Caixa (.xlsx)",
type=["xlsx"]
)

if uploaded_file is None:
st.warning("Envie o arquivo para iniciar a análise.")
st.stop()

try:
df_raw = pd.read_excel(uploaded_file)
except:
st.error("Erro ao ler o arquivo Excel.")
st.stop()

# ------------------------------

# Detectar colunas de números

# ------------------------------

cols = [
c for c in df_raw.columns
if "bola" in c.lower() or "dezena" in c.lower()
]

if len(cols) == 0:
st.error("Não foi possível detectar colunas de números.")
st.stop()

df = df_raw[cols].copy()

df = df.apply(pd.to_numeric, errors="coerce")
df = df.dropna()

numeros = df.values.flatten().astype(int)

max_num = int(np.max(numeros))

st.sidebar.header("Configuração")

tipo = st.sidebar.selectbox(
"Tipo de jogo",
["Mega-Sena", "Lotofácil"]
)

if tipo == "Mega-Sena":
total = 60
jogo_n = 6
else:
total = 25
jogo_n = 15

nums = list(range(1, total + 1))

# ------------------------------

# Frequência histórica

# ------------------------------

st.header("📊 Frequência Histórica")

freq = Counter(numeros)

freq_df = pd.DataFrame({
"numero": nums,
"freq": [freq.get(i, 0) for i in nums]
})

fig = px.bar(freq_df, x="numero", y="freq")

st.plotly_chart(fig, use_container_width=True)

# ------------------------------

# Entropia

# ------------------------------

st.header("🧮 Entropia do Sistema")

prob = freq_df["freq"] / freq_df["freq"].sum()

ent = entropy(prob)

st.metric("Entropia de Shannon", round(ent, 4))

# ------------------------------

# Atraso

# ------------------------------

st.header("⏳ Atraso das Dezenas")

delay = {}

for n in nums:

```
atraso = 0

for i in range(len(df) - 1, -1, -1):

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

# ------------------------------

# Co-ocorrência

# ------------------------------

st.header("🔥 Co-ocorrência entre Números")

matrix = np.zeros((total, total))

for row in df.values:

```
for a in row:
    for b in row:

        if a != b:
            matrix[a - 1][b - 1] += 1
```

fig = px.imshow(matrix)

st.plotly_chart(fig, use_container_width=True)

# ------------------------------

# Machine Learning

# ------------------------------

st.header("🤖 Estimativa de Probabilidade (Random Forest)")

X = []
y = []

for i in range(len(df) - 1):

```
atual = df.iloc[i].values
prox = df.iloc[i + 1].values

for n in nums:

    X.append([1 if n in atual else 0])
    y.append(1 if n in prox else 0)
```

X = np.array(X)
y = np.array(y)

model = RandomForestClassifier(
n_estimators=200,
random_state=42
)

model.fit(X, y)

probs = []

for n in nums:

```
p = model.predict_proba([[0]])[0][1]

probs.append(p)
```

prob_df = pd.DataFrame({
"numero": nums,
"prob": probs
})

fig = px.bar(prob_df, x="numero", y="prob")

st.plotly_chart(fig, use_container_width=True)

# ------------------------------

# Monte Carlo

# ------------------------------

st.header("🎲 Simulação Monte Carlo")

sim = st.slider(
"Número de simulações",
1000,
50000,
10000
)

result = []

for _ in range(sim):

```
jogo = random.sample(nums, jogo_n)

score = sum(freq.get(n, 0) for n in jogo)

result.append((jogo, score))
```

result.sort(key=lambda x: x[1], reverse=True)

top = result[:20]

st.subheader("Top jogos simulados")

for j, s in top:
st.write(sorted(j))

# ------------------------------

# Algoritmo Genético

# ------------------------------

st.header("🧬 Gerador Evolutivo de Jogos")

def fitness(jogo):

```
f = sum(freq.get(n, 0) for n in jogo)
d = sum(delay.get(n, 0) for n in jogo)

return f * 0.7 + d * 0.3
```

pop = 40

population = [
random.sample(nums, jogo_n)
for _ in range(pop)
]

for _ in range(60):

```
population = sorted(
    population,
    key=fitness,
    reverse=True
)

new_pop = population[:10]

while len(new_pop) < pop:

    p1 = random.choice(population[:20])
    p2 = random.choice(population[:20])

    cut = random.randint(1, jogo_n - 1)

    child = list(set(p1[:cut] + p2[cut:]))

    while len(child) < jogo_n:

        n = random.choice(nums)

        if n not in child:
            child.append(n)

    new_pop.append(child)

population = new_pop
```

best = sorted(
population,
key=fitness,
reverse=True
)[:10]

st.subheader("Top jogos evolutivos")

for j in best:

```
st.success(
    " | ".join(f"{n:02d}" for n in sorted(j))
)
```

# ------------------------------

# Backtesting

# ------------------------------

st.header("🧪 Backtesting")

pool = list(
prob_df
.sort_values("prob", ascending=False)
["numero"]
[:30]
)

hits = []

for i in range(len(df) - 1):

```
real = set(df.iloc[i + 1].values)

jogo = set(
    random.sample(pool, jogo_n)
)

hits.append(len(real & jogo))
```

media = np.mean(hits)

st.metric("Média de acertos simulada", round(media, 2))

fig = px.histogram(hits)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

st.caption(
"""
⚠️ Aviso científico: Loterias ideais são processos aleatórios independentes.
Este aplicativo serve apenas para análise estatística exploratória.
"""
)
