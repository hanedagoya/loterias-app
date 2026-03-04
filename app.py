import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import chisquare

st.set_page_config(page_title="Loterias - Análise Estatística", layout="wide")

st.title("📊 Análise Estatística - Mega-Sena & Lotofácil")

# ===============================
# Escolha da Loteria
# ===============================

loteria = st.sidebar.selectbox(
    "Escolha a Loteria",
    ["Mega-Sena", "Lotofácil"]
)

if loteria == "Mega-Sena":
    total_numeros = 60
    dezenas = 6
else:
    total_numeros = 25
    dezenas = 15

concursos = 3000

# ===============================
# Simulação (corrigida)
# ===============================

@st.cache_data
def simular(total_numeros, dezenas, concursos):
    jogos = [
        np.random.choice(range(1, total_numeros + 1),
                         dezenas,
                         replace=False)
        for _ in range(concursos)
    ]
    return pd.DataFrame(jogos)

df = simular(total_numeros, dezenas, concursos)

# ===============================
# Estatísticas
# ===============================

valores = df.values.flatten()
freq = pd.Series(valores).value_counts().sort_index()

soma = df.sum(axis=1)
pares = df.apply(lambda x: sum(n % 2 == 0 for n in x), axis=1)

stat, p = chisquare(freq, [freq.sum()/total_numeros]*total_numeros)

col1, col2, col3 = st.columns(3)

col1.metric("Média da Soma", round(soma.mean(), 2))
col2.metric("Média de Pares", round(pares.mean(), 2))
col3.metric("p-value Qui²", round(p, 4))

# ===============================
# Gráfico
# ===============================

st.subheader("Frequência dos Números")

fig, ax = plt.subplots()
ax.bar(freq.index, freq.values)
st.pyplot(fig)

# ===============================
# Gerador de Jogo
# ===============================

st.subheader("🎲 Gerar Jogo Aleatório")

if st.button("Gerar Jogo"):
    jogo = sorted(np.random.choice(range(1, total_numeros + 1),
                                   dezenas,
                                   replace=False))
    
    jogo_formatado = [int(n) for n in jogo]
    
    st.success(" | ".join(f"{n:02d}" for n in jogo_formatado))

