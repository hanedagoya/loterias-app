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
Ferramenta experimental baseada em:

• Estatística clássica
• Teoria da informação
• Machine Learning
• Simulação Monte Carlo
• Algoritmos evolutivos
""")

uploaded_file = st.file_uploader("Envie o arquivo oficial da Caixa (.xlsx)", type=["xlsx"])

if uploaded_file is None:
st.stop()

df = pd.read_excel(uploaded_file)

# detectar colunas de números

cols = [c for c in df.columns if "bola" in c.lower() or "dezena" in c.lower()]
df = df[cols]

numeros = df.values.flatten()

max_num = int(np.max(numeros))

st.sidebar.header("Configuração")

tipo = st.sidebar.selectbox("Tipo de jogo", ["Mega-Sena", "Lotofácil"])

if tipo == "Mega-Sena":
total = 60
jogo_n = 6
else:
total = 25
jogo_n = 15

# ---------------------------------

# Frequência

# ---------------------------------

st.header("📊 Frequência Histórica")

freq = Counter(numeros)

freq_df = pd.DataFrame({
"numero": list(range(1,total+1)),
"freq":[freq.get(i,0) for i in range(1,total+1)]
})

fig = px.bar(freq_df,x="numero",y="freq")
st.plotly_chart(fig,use_container_width=True)

# ---------------------------------

# Entropia

# ---------------------------------

st.header("🧮 Entropia do sistema")

prob = freq_df["freq"]/freq_df["freq"].sum()
ent = entropy(prob)

st.write("Entropia de Shannon:",round(ent,4))

# ---------------------------------

# Atraso de números

# ---------------------------------

st.header("⏳ Atraso das dezenas")

delay = {}

for n in range(1,total+1):
for i in range(len(df)-1,-1,-1):
if n in df.iloc[i].values:
delay[n]=len(df)-i
break

delay_df = pd.DataFrame({
"numero":list(delay.keys()),
"atraso":list(delay.values())
})

fig = px.bar(delay_df,x="numero",y="atraso")
st.plotly_chart(fig,use_container_width=True)

# ---------------------------------

# Co-ocorrência

# ---------------------------------

st.header("🔥 Co-ocorrência entre números")

matrix = np.zeros((total,total))

for row in df.values:
for a in row:
for b in row:
if a!=b:
matrix[a-1][b-1]+=1

fig = px.imshow(matrix)
st.plotly_chart(fig,use_container_width=True)

# ---------------------------------

# Machine Learning

# ---------------------------------

st.header("🤖 Probabilidade com Random Forest")

X=[]
y=[]

for i in range(len(df)-1):

```
atual=df.iloc[i].values
prox=df.iloc[i+1].values

for n in range(1,total+1):

    X.append([n in atual])
    y.append(int(n in prox))
```

X=np.array(X)
y=np.array(y)

model=RandomForestClassifier(n_estimators=200)
model.fit(X,y)

probs=[]

for n in range(1,total+1):
p=model.predict_proba([[False]])[0][1]
probs.append(p)

prob_df=pd.DataFrame({
"numero":range(1,total+1),
"prob":probs
})

fig=px.bar(prob_df,x="numero",y="prob")
st.plotly_chart(fig,use_container_width=True)

# ---------------------------------

# Monte Carlo

# ---------------------------------

st.header("🎲 Simulação Monte Carlo")

sim=st.slider("Simulações",1000,200000,20000)

nums=list(range(1,total+1))

result=[]

for _ in range(sim):

```
jogo=random.sample(nums,jogo_n)

score=sum(freq[n] for n in jogo)

result.append((jogo,score))
```

result.sort(key=lambda x:x,reverse=True)

top=result[:20]

st.subheader("Melhores jogos simulados")

for j,s in top:
st.write(j)

# ---------------------------------

# Algoritmo Genético

# ---------------------------------

st.header("🧬 Gerador Evolutivo de Jogos")

def fitness(jogo):

```
f=sum(freq[n] for n in jogo)
d=sum(delay[n] for n in jogo)

return f*0.7 + d*0.3
```

pop=50

population=[random.sample(nums,jogo_n) for _ in range(pop)]

for _ in range(100):

```
population=sorted(population,key=fitness,reverse=True)

new_pop=population[:10]

while len(new_pop)<pop:

    p1=random.choice(population[:20])
    p2=random.choice(population[:20])

    cut=random.randint(1,jogo_n-1)

    child=list(set(p1[:cut]+p2[cut:]))

    while len(child)<jogo_n:
        n=random.choice(nums)
        if n not in child:
            child.append(n)

    new_pop.append(child)

population=new_pop
```

best=sorted(population,key=fitness,reverse=True)[:10]

st.subheader("Top jogos evolutivos")

for j in best:
st.success(" | ".join(f"{n:02d}" for n in sorted(j)))

# ---------------------------------

# Backtesting

# ---------------------------------

st.header("🧪 Backtesting")

hits=[]

pool=list(prob_df.sort_values("prob",ascending=False)["numero"][:30])

for i in range(len(df)-1):

```
real=set(df.iloc[i+1].values)

jogo=set(random.sample(pool,jogo_n))

hits.append(len(real & jogo))
```

st.write("Média de acertos:",round(np.mean(hits),2))

fig=px.histogram(hits)
st.plotly_chart(fig,use_container_width=True)
