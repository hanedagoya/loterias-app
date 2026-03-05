import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from collections import Counter

st.set_page_config(page_title="Análise de Loterias", layout="wide")

st.title("📊 Análise Estatística de Loterias")

st.write("Upload do arquivo oficial da Caixa (.xlsx)")

uploaded_file = st.file_uploader("Arquivo", type=["xlsx"])

if uploaded_file is None:
st.stop()

try:
df = pd.read_excel(uploaded_file)
except:
st.error("Erro ao ler o arquivo.")
st.stop()

# detectar colunas de dezenas automaticamente

cols = []

for c in df.columns:
name = str(c).lower()
if "bola" in name or "dezena" in name:
cols.append(c)

if len(cols) == 0:
st.error("Não foi possível identificar as colunas de dezenas.")
st.stop()

df = df[cols]

df = df.apply(pd.to_numeric, errors="coerce")

df = df.dropna()

numeros = df.values.flatten().astype(int)

st.subheader("Quantidade de sorteios")
st.write(len(df))

# frequência

freq = Counter(numeros)

max_num = max(numeros)

freq_list = [freq.get(i,0) for i in range(1,max_num+1)]

freq_df = pd.DataFrame({
"numero": range(1,max_num+1),
"frequencia": freq_list
})

st.subheader("Frequência dos números")

fig = px.bar(freq_df, x="numero", y="frequencia")

st.plotly_chart(fig, use_container_width=True)

# números mais frequentes

top = freq_df.sort_values("frequencia", ascending=False).head(10)

st.subheader("Top 10 números")

st.dataframe(top)

# gerador simples

st.subheader("Gerador de jogo aleatório")

qtd = st.slider("Quantidade de números", 6, 15, 6)

if st.button("Gerar jogo"):

```
nums = list(range(1, max_num+1))

jogo = np.random.choice(nums, qtd, replace=False)

jogo = sorted(jogo)

st.success(" | ".join(f"{n:02d}" for n in jogo))
```
