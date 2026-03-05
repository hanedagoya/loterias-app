import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from collections import Counter

st.set_page_config(page_title="Análise de Loterias", layout="wide")

st.title("📊 Análise Estatística de Loterias")

st.write("Faça upload do arquivo oficial da Caixa (.xlsx)")

uploaded_file = st.file_uploader("Arquivo", type=["xlsx"])

if uploaded_file is None:
st.warning("Envie um arquivo para continuar.")
st.stop()

try:
df = pd.read_excel(uploaded_file)
except Exception:
st.error("Erro ao ler o arquivo Excel.")
st.stop()

# Detectar colunas com dezenas automaticamente

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

st.subheader("Quantidade de concursos analisados")
st.write(len(df))

# Frequência das dezenas

freq = Counter(numeros)

max_num = int(max(numeros))

freq_df = pd.DataFrame({
"numero": list(range(1, max_num + 1)),
"frequencia": [freq.get(i, 0) for i in range(1, max_num + 1)]
})

st.subheader("Frequência das dezenas")

fig = px.bar(freq_df, x="numero", y="frequencia")

st.plotly_chart(fig, use_container_width=True)

# Top números

top = freq_df.sort_values("frequencia", ascending=False).head(10)

st.subheader("Top 10 dezenas mais frequentes")

st.dataframe(top)

# Gerador de jogo

st.subheader("Gerador de jogo aleatório")

qtd = st.slider("Quantidade de dezenas", 6, 15, 6)

if st.button("Gerar jogo"):
nums = list(range(1, max_num + 1))
jogo = np.random.choice(nums, qtd, replace=False)
jogo = sorted(jogo)
st.success(" | ".join(f"{n:02d}" for n in jogo))
