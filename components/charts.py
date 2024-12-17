import plotly.express as px
import pandas as pd
import streamlit as st
import itables
from utils.functions import display_metrics

def create_comparative_chart_with_tabs(data, cidades, indicadores, periodo_anual, ano_selecionado):
    """
    Cria gráficos comparativos organizados em abas para os indicadores selecionados.
    """
    # Mapeamento de meses para valores numéricos
    meses_ordenados = {
        "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4, "Maio": 5, "Junho": 6,
        "Julho": 7, "Agosto": 8, "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
    }

    # Garantir que as colunas `Mês` e `Ano` estão preenchidas
    data["Mês"] = data["Mês"].fillna("Indefinido")
    data["Ano"] = data["Ano"].fillna("Indefinido")

    # Criar colunas auxiliares `Mês_Num` e `Período`
    data["Mês_Num"] = data["Mês"].map(meses_ordenados).fillna(0).astype(int)
    data["Período"] = data["Mês"] + "/" + data["Ano"]

    # Filtrar dados por cidades e indicadores
    filtered_data = data[data["Cidade"].isin(cidades) & data["Sigla"].isin(indicadores)]

    # Filtrar dados para gráficos mensais e anuais
    if periodo_anual:
        filtered_data = filtered_data[filtered_data["Ano"] != "Indefinido"]  # Ignorar anos indefinidos
    else:
        filtered_data = filtered_data[
            (filtered_data["Mês"] != "Indefinido") & (filtered_data["Ano"] != "Indefinido")
        ]  # Ignorar meses e anos indefinidos

    # Garantir que `Período` seja válido
    filtered_data = filtered_data[~filtered_data["Período"].str.contains("Indefinido|Indefinido")]

    # Criar abas para os indicadores
    tabs = st.tabs(indicadores)

    filtered_data = filtered_data.sort_values(['Sigla','Mês_Num','Ano','Cidade'])

    # Gerar gráficos para cada indicador
    for tab, indicador in zip(tabs, indicadores):
        with tab:
            # Filtrar os dados do indicador
            indicador_data = filtered_data[filtered_data["Sigla"] == indicador]

            # Obter o título e unidade do indicador diretamente do DataFrame consolidado
            if not indicador_data.empty:
                titulo = indicador_data["Título"].iloc[0]
                unidade = indicador_data["Unidade"].iloc[0]
            else:
                titulo = "Dados não disponíveis"
                unidade = ""

            # Exibir o título e unidade do indicador
            st.markdown(f"### {indicador}: {titulo} ({unidade})")

            if indicador_data.empty:
                st.write("Nenhum dado disponível para este indicador.")
                continue

            st.write('Meta:')

            display_metrics(indicador, int(ano_selecionado), indicador_data['IBGE'])

            if periodo_anual:
                # Gráfico de barras para dados anuais
                fig = px.bar(
                    indicador_data,
                    x="Ano",
                    y="Valor",
                    color="Cidade",
                    barmode="group",
                    title=f"Comparação Anual para {indicador}",
                    labels={"Valor": "Valor", "Ano": "Ano"}
                )
                fig.update_layout(xaxis=dict(title="Ano"), yaxis=dict(title="Valor"))
                st.plotly_chart(fig, use_container_width=True)
            else:
                # Garantir a ordem correta no eixo x
                category_order = sorted(
                    indicador_data["Período"].unique(),
                    key=lambda x: (
                        int(x.split("/")[1]),  # Ano
                        meses_ordenados.get(x.split("/")[0], 0)  # Mês
                    )
                )
                # Gráfico de linhas para dados mensais
                fig = px.line(
                    indicador_data,
                    x="Período",
                    y="Valor",
                    text="Valor",
                    color="Cidade",
                    markers=True,
                    title=f"Comparação Mensal para {indicador}",
                    labels={"Valor": "Valor", "Período": "Período"},
                    category_orders={"Período": category_order},
                )
                fig.update_traces(textposition="bottom right")
                fig.update_layout(
                    xaxis=dict(title="Período", tickangle=45),
                    yaxis=dict(title="Valor"),
                )
                st.plotly_chart(fig, use_container_width=True)

                st.write(indicador_data[['Cidade','Período', 'Valor']])

def create_comparative_chart_with_tabs_microrregioes(data, microrregioes, indicadores, periodo_anual, ano_selecionado):
    """
    Cria gráficos comparativos organizados em abas para os indicadores selecionados, adaptados para microrregiões.
    """
    # Mapeamento de meses para valores numéricos
    meses_ordenados = {
        "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4, "Maio": 5, "Junho": 6,
        "Julho": 7, "Agosto": 8, "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
    }

    # Garantir que as colunas `Mês` e `Ano` estão preenchidas
    data["Mês"] = data["Mês"].fillna("Indefinido")
    data["Ano"] = data["Ano"].fillna("Indefinido")

    # Criar colunas auxiliares `Mês_Num` e `Período`
    data["Mês_Num"] = data["Mês"].map(meses_ordenados).fillna(0).astype(int)
    data["Período"] = data["Mês"] + "/" + data["Ano"]

    # Filtrar dados por microrregiões e indicadores
    filtered_data = data[data["Microrregião"].isin(microrregioes) & data["Sigla"].isin(indicadores)]
    # Filtrar dados para gráficos mensais e anuais
    if periodo_anual:
        filtered_data = filtered_data[filtered_data["Ano"] != "Indefinido"]  # Ignorar anos indefinidos
    else:
        filtered_data = filtered_data[
            (filtered_data["Mês"] != "Indefinido") & (filtered_data["Ano"] != "Indefinido")
        ]  # Ignorar meses e anos indefinidos

    # Garantir que `Período` seja válido
    filtered_data = filtered_data[~filtered_data["Período"].str.contains("Indefinido|Indefinido")]
    filtered_data = filtered_data.sort_values(['Sigla','Mês_Num','Ano'])
    # Criar abas para os indicadores
    tabs = st.tabs(indicadores)

    # Gerar gráficos para cada indicador
    for tab, indicador in zip(tabs, indicadores):
        with tab:
            # Filtrar os dados do indicador
            indicador_data = filtered_data[filtered_data["Sigla"] == indicador]
            # Obter o título e unidade do indicador diretamente do DataFrame consolidado
            if not indicador_data.empty:
                titulo = indicador_data["Título"].iloc[0]
                unidade = indicador_data["Unidade"].iloc[0]
            else:
                titulo = "Dados não disponíveis"
                unidade = ""

            # Exibir o título e unidade do indicador
            st.markdown(f"### {indicador}: {titulo} ({unidade})")

            if indicador_data.empty:
                st.write("Nenhum dado disponível para este indicador.")
                continue
            
            display_metrics(indicador, int(ano_selecionado))
            
            if periodo_anual:
                # Gráfico de barras para dados anuais
                fig = px.bar(
                    indicador_data,
                    x="Ano",
                    y="Valor",
                    color="Microrregião",
                    barmode="group",
                    title=f"Comparação Anual para {indicador}",
                    labels={"Valor": "Valor", "Ano": "Ano"}
                )
                fig.update_layout(xaxis=dict(title="Ano"), yaxis=dict(title="Valor"))
                st.plotly_chart(fig, use_container_width=True)
            else:
                # Garantir a ordem correta no eixo x
                category_order = sorted(
                    indicador_data["Período"].unique(),
                    key=lambda x: (
                        int(x.split("/")[1]),  # Ano
                        meses_ordenados.get(x.split("/")[0], 0)  # Mês
                    )
                )
                # Gráfico de linhas para dados mensais
                fig = px.line(
                    indicador_data,
                    x="Período",
                    y="Valor",
                    text="Valor",
                    color="Microrregião",
                    markers=True,
                    title=f"Comparação Mensal para {indicador}",
                    labels={"Valor": "Valor", "Período": "Período"},
                    category_orders={"Período": category_order},
                )
                fig.update_layout(
                    xaxis=dict(title="Período", tickangle=45),
                    yaxis=dict(title="Valor"),
                )
                fig.update_traces(textposition="bottom right")
                st.plotly_chart(fig, use_container_width=True)

                st.write(indicador_data[['Microrregião','Período', 'Valor']])
                #st.dataframe(indicador_data[['Período','Valor']])
                #st.dataframe(indicador_data.style.hide(axis="index"))
                #st.markdown(indicador_data.style.hide(axis="index").to_html(), unsafe_allow_html=True)
                #indicador_data_table=pd.DataFrame(indicador_data[['Período','Valor']])
                #st.components.v1.html(itables.to_html_datatable(indicador_data_table), height=400)