import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path



st.set_page_config(page_title="Indicador 7 — Meio de transporte", layout="wide")
sns.set_style("whitegrid")

st.title("Indicador 7 — Meio de transporte")
st.header("Deslocamento ao trabalho por cor ou raça — 2022")
st.write("Distribuição percentual das mulheres de 10 anos ou mais, ocupadas na semana de referência.")
st.write("Considera o transporte em que passam mais tempo no deslocamento ao trabalho principal.")



caminho_ficheiro = Path(__file__).parent / "Tabela_13_Meio_de_transporte.xlsx"

if not caminho_ficheiro.exists():
    st.write("Coloque Tabela_13_Meio_de_transporte.xlsx na mesma pasta deste arquivo Python.")
    st.stop()

df = pd.read_excel(caminho_ficheiro, sheet_name="BR GR UF MU", skiprows=3, header=None)

grupos = ["Branca", "Preta ou parda", "Indígena"]
transportes = [
    "A pé", "Bicicleta", "Motocicleta ou Mototaxi",
    "Automóvel, taxi ou assemelhados", "Transporte coletivo", "Outros"
]

colunas = ["Local"]
for grupo in grupos:
    for transporte in transportes:
        colunas.append(f"{grupo}_{transporte}")

df = df.iloc[:, :19]
df.columns = colunas
df["Local"] = df["Local"].astype(str).str.strip()



df_longo = df.melt(
    id_vars=["Local"],
    value_vars=colunas[1:],
    var_name="Categoria",
    value_name="Percentual"
)


df_longo["Percentual"] = pd.to_numeric(df_longo["Percentual"], errors="coerce")
df_longo[["Cor ou raça", "Transporte"]] = df_longo["Categoria"].str.split("_", expand=True)

regioes = ["Norte", "Nordeste", "Sudeste", "Sul", "Centro-oeste"]
estados = [
    "Rondônia", "Acre", "Amazonas", "Roraima", "Pará", "Amapá", "Tocantins",
    "Maranhão", "Piauí", "Ceará", "Rio Grande do Norte", "Paraíba", "Pernambuco",
    "Alagoas", "Sergipe", "Bahia", "Minas Gerais", "Espírito Santo",
    "Rio de Janeiro", "São Paulo", "Paraná", "Santa Catarina", "Rio Grande do Sul",
    "Mato Grosso do Sul", "Mato Grosso", "Goiás", "Distrito Federal"
]

municipios = sorted(df.loc[~df["Local"].isin(["Brasil"] + regioes + estados), "Local"].tolist())
locais_por_nivel = {
    "Brasil": ["Brasil"],
    "Grandes regiões": regioes,
    "Estados": estados,
    "Municípios": municipios
}



st.write("______________________________________________")
st.subheader("Filtros do dashboard")

coluna1, coluna2 = st.columns([1, 2])
nivel = coluna1.selectbox("Tipo de local:", list(locais_por_nivel.keys()))
local = coluna2.selectbox("Selecione o local:", locais_por_nivel[nivel])
grupos_escolhidos = st.multiselect("Selecione a cor ou raça:", grupos, default=grupos)

if not grupos_escolhidos:
    st.write("Selecione pelo menos um grupo para visualizar os dados.")
    st.stop()

df_local = df_longo[
    (df_longo["Local"] == local) &
    (df_longo["Cor ou raça"].isin(grupos_escolhidos))
].copy()

st.write("Local selecionado:", local)
st.write("Os percentuais são de cada grupo separadamente; não representam quantidades de pessoas.")



st.subheader("Transporte com maior percentual")
colunas_resumo = st.columns(len(grupos_escolhidos))

for i, grupo in enumerate(grupos_escolhidos):
    dados_grupo = df_local[df_local["Cor ou raça"] == grupo].dropna(subset=["Percentual"])
    colunas_resumo[i].subheader(grupo)

    if dados_grupo.empty:
        colunas_resumo[i].write("Sem dados informados para este grupo.")
    else:
        maior = dados_grupo.loc[dados_grupo["Percentual"].idxmax()]
        colunas_resumo[i].write(maior["Transporte"])
        colunas_resumo[i].title(f"{maior['Percentual']:.1f}%")



st.write("______________________________________________")
st.subheader("Comparação dos meios de transporte")
dados_grafico = df_local.dropna(subset=["Percentual"])

if dados_grafico.empty:
    st.write("Não há valores informados para os filtros escolhidos.")
else:
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(
        data=dados_grafico, x="Percentual", y="Transporte", hue="Cor ou raça",
        order=transportes, hue_order=grupos_escolhidos,
        palette={"Branca": "#4c78a8", "Preta ou parda": "#f58518", "Indígena": "#54a24b"},
        ax=ax
    )
    ax.set_title(f"Meio de transporte — {local}")
    ax.set_xlabel("Percentual (%)")
    ax.set_ylabel("Meio de transporte")
    ax.set_xlim(0, 100)
    ax.legend(title="Cor ou raça", loc="lower right")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)



tabela = df_local.pivot(index="Transporte", columns="Cor ou raça", values="Percentual")
tabela = tabela.reindex(index=transportes, columns=grupos_escolhidos)
st.subheader("Dados do local selecionado (%)")
st.write(tabela.round(1))
st.write("Valores ausentes na tabela não foram informados na planilha e não são considerados zero.")



if "Branca" in grupos_escolhidos and "Preta ou parda" in grupos_escolhidos:
    st.subheader("Diferença entre Branca e Preta ou parda")
    diferenca = tabela["Branca"] - tabela["Preta ou parda"]
    diferenca = diferenca.dropna()

    if diferenca.empty:
        st.write("Não há dados suficientes para calcular a diferença.")
    else:
        fig, ax = plt.subplots(figsize=(12, 5))
        cores = ["#4c78a8" if valor >= 0 else "#f58518" for valor in diferenca.values]
        ax.barh(diferenca.index, diferenca.values, color=cores)
        ax.axvline(0, color="black", linewidth=1)
        ax.invert_yaxis()
        ax.set_title(f"Branca menos Preta ou parda — {local}")
        ax.set_xlabel("Diferença em pontos percentuais (p.p.)")
        ax.set_ylabel("Meio de transporte")
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    st.write("Valor positivo: percentual maior no grupo Branca. Valor negativo: maior no grupo Preta ou parda.")



st.write("______________________________________________")
st.subheader("Ranking por meio de transporte")

coluna1, coluna2, coluna3 = st.columns(3)
nivel_ranking = coluna1.selectbox("Comparar:", ["Estados", "Municípios", "Grandes regiões"])
grupo_ranking = coluna2.selectbox("Cor ou raça do ranking:", grupos_escolhidos)
transporte_ranking = coluna3.selectbox("Meio de transporte:", transportes, index=4)
quantidade = st.number_input("Quantidade de locais no gráfico:", min_value=3, max_value=20, value=10, step=1)

ranking = df_longo[
    (df_longo["Local"].isin(locais_por_nivel[nivel_ranking])) &
    (df_longo["Cor ou raça"] == grupo_ranking) &
    (df_longo["Transporte"] == transporte_ranking)
].dropna(subset=["Percentual"])

ranking = ranking.sort_values("Percentual", ascending=False)

if ranking.empty:
    st.write("Não há dados informados para este ranking.")
else:
    maior = ranking.iloc[0]
    menor = ranking.iloc[-1]
    st.write(f"Maior percentual: {maior['Local']} — {maior['Percentual']:.1f}%")
    st.write(f"Menor percentual: {menor['Local']} — {menor['Percentual']:.1f}%")
    st.write("Em caso de empate, os locais empatados têm o mesmo percentual.")

    top = ranking.head(int(quantidade))
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.barh(top["Local"], top["Percentual"], color="#4c78a8")
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_title(f"Maiores percentuais — {transporte_ranking} — {grupo_ranking}")
    ax.set_xlabel("Percentual (%)")
    ax.set_ylabel("Local")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
    st.write(top[["Local", "Percentual"]].reset_index(drop=True))



st.write("______________________________________________")
st.write("Fonte: Tabela_13_Meio_de_transporte.xlsx — aba BR GR UF MU — dados de 2022.")
