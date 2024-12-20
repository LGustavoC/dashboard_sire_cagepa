import plotly.express as px
import pandas as pd
import streamlit as st
import itables
from utils.functions import display_metrics
import numpy as np

def create_annual_bar_chart(data, cidades, indicadores, ano_selecionado):
    """
    Cria gráficos de barras organizados para os indicadores selecionados no período anual.
    """
    # Filtrar os dados para período anual (sem mês especificado)
    filtered_data = data[
        data["Cidade"].isin(cidades) & 
        data["Sigla"].isin(indicadores) & 
        (data["Mês"].isna() | (data["Mês"] == "Indefinido")) & 
        (data["Ano"] == str(ano_selecionado))
    ]

    # Criar abas para os indicadores
    tabs = st.tabs(indicadores)

    for tab, indicador in zip(tabs, indicadores):
        with tab:
            # Filtrar dados para o indicador
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
                st.write("Nenhum dado disponível para este indicador no ano selecionado.")
                continue

            # Gráfico de barras para dados anuais
            fig = px.bar(
                indicador_data,
                x="Cidade",
                y="Valor",
                text="Valor",
                color="Cidade",  # Diferenciar as barras pelas cidades
                title=f"Comparação Anual para {indicador} ({ano_selecionado})",
                labels={"Valor": "Valor", "Cidade": "Cidade"}
            )
            fig.update_traces(textposition="outside")
            fig.update_layout(
                xaxis=dict(title="Cidade", tickangle=45),
                yaxis=dict(title="Valor", range=[0, 110]),  # Ajustar o range para 0 a 100 se for percentual
                coloraxis_showscale=False  # Remover a escala de cores, se desnecessário
            )
            st.plotly_chart(fig, use_container_width=True)

            # Exibir tabela com os dados
            st.write(indicador_data[["Cidade", "Ano", "Valor"]])

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

    # Criar jitter fixo por Cidade
    jitter_map = {cidade: np.random.uniform(-0.5, 0.5) for cidade in data["Cidade"].unique()}
    data["Valor_Jitter"] = data.apply(lambda row: row["Valor"] + jitter_map[row["Cidade"]], axis=1)

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

    filtered_data = filtered_data.sort_values(['Sigla', 'Mês_Num', 'Ano', 'Cidade'])

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

            #st.write("Meta:")
            display_metrics(indicador, int(ano_selecionado), indicador_data["IBGE"])

            # Criar tabs para diferentes tipos de gráficos
            tabs_graph = st.tabs(["Gráfico Temporal", "Subgráficos"])

            with tabs_graph[0]:
                # Gráfico de linhas para dados mensais
                category_order = sorted(
                    indicador_data["Período"].unique(),
                    key=lambda x: (
                        int(x.split("/")[1]),  # Ano
                        meses_ordenados.get(x.split("/")[0], 0)  # Mês
                    )
                )
                fig_temporal = px.line(
                    indicador_data,
                    x="Período",
                    y="Valor_Jitter",  # Usar o Valor com Jitter
                    text="Valor",
                    color="Cidade",
                    markers=True,
                    title=f"Comparação Temporal para {indicador}",
                    labels={"Valor_Jitter": "Valor", "Período": "Período"},
                    category_orders={"Período": category_order},
                )
                fig_temporal.update_traces(textposition="bottom right")
                fig_temporal.update_layout(
                    xaxis=dict(title="Período", tickangle=45),
                    yaxis=dict(title="Valor", range=[0, 100]),  # Limita de 0 a 100 para percentuais
                )
                st.plotly_chart(fig_temporal, use_container_width=True)
            with tabs_graph[1]:
                # Gráfico de subgráficos para cada cidade
                fig_faceted = px.line(
                    indicador_data,
                    x="Período",
                    y="Valor",
                    color="Cidade",
                    markers=True,
                    facet_col="Cidade",
                    facet_col_wrap=3,
                    title=f"Subgráficos para {indicador}",
                    labels={"Valor": "Valor", "Período": "Período"}
                )
                fig_faceted.update_layout(
                    xaxis=dict(title="Período", tickangle=45),
                    yaxis=dict(title="Valor", range=[0, 105]),
                )
                st.plotly_chart(fig_faceted, use_container_width=True)

            st.write(indicador_data[['Cidade', 'Período', 'Valor']])

def create_annual_bar_chart_microrregioes(data, microrregioes, indicadores, ano_selecionado):
    """
    Cria gráficos de barras organizados para os indicadores selecionados no período anual, adaptados para microrregiões.
    """
    # Filtrar os dados para período anual (sem mês especificado)
    filtered_data = data[
        data["Microrregião"].isin(microrregioes) & 
        data["Sigla"].isin(indicadores) &  
        (data["Ano"] == str(ano_selecionado))
    ]

    # Criar abas para os indicadores
    tabs = st.tabs(indicadores)

    for tab, indicador in zip(tabs, indicadores):
        with tab:
            # Filtrar dados para o indicador
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
                st.write("Nenhum dado disponível para este indicador no ano selecionado.")
                continue

            # Gráfico de barras para dados anuais
            fig = px.bar(
                indicador_data,
                x="Microrregião",
                y="Valor",
                text="Valor",
                color="Microrregião",  # Diferenciar as barras pelas microrregiões
                title=f"Comparação Anual para {indicador} ({ano_selecionado})",
                labels={"Valor": "Valor", "Microrregião": "Microrregião"}
            )
            fig.update_traces(textposition="outside")
            fig.update_layout(
                xaxis=dict(title="Microrregião", tickangle=45),
                yaxis=dict(title="Valor", range=[0, 110]),  # Ajustar o range para 0 a 100 se for percentual
                coloraxis_showscale=False  # Remover a escala de cores, se desnecessário
            )
            st.plotly_chart(fig, use_container_width=True)

            # Exibir tabela com os dados
            st.write(indicador_data[["Microrregião", "Ano", "Valor"]])


def create_comparative_chart_with_tabs_microrregioes(data, microrregioes, indicadores, periodo_anual, ano_selecionado):
    """
    Cria gráficos comparativos organizados em abas para os indicadores selecionados, adaptados para microrregiões, com Jitter.
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
    filtered_data = filtered_data.sort_values(['Sigla', 'Mês_Num', 'Ano'])

    # Adicionar coluna Jitter para evitar sobreposição
    jitter_values = {}
    for microrregiao in filtered_data["Microrregião"].unique():
        jitter = 0
        for idx in filtered_data[filtered_data["Microrregião"] == microrregiao].index:
            jitter_values[idx] = jitter
            jitter += 0.2  # Incremento do Jitter para diferenciar as linhas
    filtered_data["Valor_Jitter"] = filtered_data.index.map(jitter_values).fillna(0) + filtered_data["Valor"]

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
            
            # Exibir métricas
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
                # Gráfico de linhas para dados mensais com Jitter
                fig = px.line(
                    indicador_data,
                    x="Período",
                    y="Valor_Jitter",
                    text="Valor",
                    color="Microrregião",
                    markers=True,
                    title=f"Comparação Mensal para {indicador}",
                    labels={"Valor_Jitter": "Valor (com Jitter)", "Período": "Período"},
                    category_orders={"Período": category_order},
                )
                fig.update_layout(
                    xaxis=dict(title="Período", tickangle=45),
                    yaxis=dict(title="Valor", range=[0, 105]),
                )
                fig.update_traces(textposition="bottom right")
                st.plotly_chart(fig, use_container_width=True)

                st.write(indicador_data[['Microrregião', 'Período', 'Valor']])

                #st.dataframe(indicador_data[['Período','Valor']])
                #st.dataframe(indicador_data.style.hide(axis="index"))
                #st.markdown(indicador_data.style.hide(axis="index").to_html(), unsafe_allow_html=True)
                #indicador_data_table=pd.DataFrame(indicador_data[['Período','Valor']])
                #st.components.v1.html(itables.to_html_datatable(indicador_data_table), height=400)