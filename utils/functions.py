import streamlit as st
import pandas as pd
import numpy as np

def show_tabs_for_municipio(data, municipio):
    """
    Exibe os indicadores do município selecionado em abas dentro do layout principal do Streamlit.
    """
    st.markdown(f"### Indicadores para {municipio}")

    # Criar abas dinâmicas para cada indicador
    indicadores = data["Sigla"].unique()
    tabs = st.tabs(indicadores)

    for tab, indicador in zip(tabs, indicadores):
        with tab:
            # Filtrar os dados para o indicador atual
            tab_data = data[data["Sigla"] == indicador][["Ano", "Mês", "Valor"]]
            tab_data = tab_data.sort_values(by=["Ano", "Mês"])  # Ordenar por período
            st.dataframe(tab_data, use_container_width=True)

def dotRemove(word):
    word = word.replace(".", '')
    return word

def changeMax(value):
    if value>100:
        value = 100
    return value

def agrupar_dados_por_microrregiao(indicator_data, microrregioes, operacoes, is_anual):
    """
    Agrupa os dados das cidades para formar os dados consolidados por microrregião, com valores arredondados para cima.
    
    Args:
        indicator_data (pd.DataFrame): DataFrame com os dados dos indicadores.
        microrregioes (dict): Dicionário mapeando as microrregiões para os IBGEs das cidades.
        operacoes (dict): Dicionário que define a operação (ex: "mean", "sum") para cada Sigla.
    
    Returns:
        pd.DataFrame: DataFrame consolidado com os dados por microrregião.
    """
    microrregiao_data = []

    for microrregiao, ibges in microrregioes.items():
        # Filtrar os dados das cidades pertencentes à microrregião
        cidades_data = indicator_data[indicator_data["IBGE"].isin(ibges)]
        
        # Agrupar os dados por Sigla, Ano e Mês, aplicando a operação definida
        for sigla, operacao in operacoes.items():
            # Filtrar os dados por indicador (Sigla)
            sigla_data = cidades_data[cidades_data["Sigla"] == sigla]
            if(is_anual):
                # Aplicar a operação
                if operacao == "mean":
                    agrupado = sigla_data.groupby(["Ano"]).agg({"Valor": "mean"}).reset_index()
                elif operacao == "sum":
                    agrupado = sigla_data.groupby(["Ano"]).agg({"Valor": "sum"}).reset_index()
                else:
                    raise ValueError(f"Operação '{operacao}' não suportada para o indicador '{sigla}'.")
            else:
                # Aplicar a operação
                if operacao == "mean":
                    agrupado = sigla_data.groupby(["Ano", "Mês"]).agg({"Valor": "mean"}).reset_index()
                elif operacao == "sum":
                    agrupado = sigla_data.groupby(["Ano", "Mês"]).agg({"Valor": "sum"}).reset_index()
                else:
                    raise ValueError(f"Operação '{operacao}' não suportada para o indicador '{sigla}'.")

            # Arredondar os valores para cima com uma casa decimal
            agrupado["Valor"] = np.ceil(agrupado["Valor"] * 10) / 10

            # Adicionar as colunas adicionais
            agrupado["Sigla"] = sigla
            agrupado["Microrregião"] = microrregiao

            microrregiao_data.append(agrupado)

    # Concatenar os dados de todas as microrregiões
    return pd.concat(microrregiao_data, ignore_index=True)


def clean_data(data, columns_to_check=None):
    """
    Limpa o DataFrame removendo duplicados e linhas com dados em branco em colunas críticas.
    
    Args:
        data (pd.DataFrame): DataFrame a ser limpo.
        columns_to_check (list, optional): Colunas a verificar para dados em branco. Se None, verifica todas.

    Returns:
        pd.DataFrame: DataFrame limpo.
    """
    # Remover duplicados
    data = data.drop_duplicates()

    # Remover linhas com valores em branco nas colunas críticas
    if columns_to_check:
        data = data.dropna(subset=columns_to_check)
    else:
        data = data.dropna()

    # Resetar o índice após a limpeza
    data = data.reset_index(drop=True)
    
    return data

def display_metrics(sigla, ano, cidades=None):
    """
    Exibe métricas diferentes usando st.metric com base na sigla e ano selecionados.
    Parâmetros:
    - sigla (str): Indicador selecionado.
    - ano (str): Ano selecionado.
    """
    # Dicionário com as métricas da meta
    metricas_meta = {
        "IN200": {2023: "≥ 99%", 2024: "≥ 99%"},
        "IN202": {2023: "≥ 70%", 2024: "≥ 70%"},
        "IN203": {2023: "≥ 70%", 2024: "≥ 70%"},
        "IN204": {2023: "---", 2024: "---"},
        "IN205": {2023: "≥ 15%", 2024: "≥ 15%"},
        "IN208": {2023: "≥ 90%", 2024: "≥ 90%"},
    }

    # Dicionário específico para IN201, que inclui IBGE
    metricas_in201 = {
        2023: {
            "2507507": "≤ 55,3%",
            "2501153": "≤ 38,13%",
            "2502300": "≤ 38,13%",
            "2503704": "≤ 38,13%",
            "2504009": "≤ 38,13%",
            "2504033": "≤ 75,00%",
            "2510600": "≤ 38,13%",
            "2510808": "≤ 38,13%",
        },
        2024: {
            "2507507": "≤ 52,3%",
            "2501153": "≤ 38,13%",
            "2502300": "≤ 38,13%",
            "2503704": "≤ 38,13%",
            "2504009": "≤ 38,13%",
            "2504033": "≤ 70,00%",
            "2510600": "≤ 38,13%",
            "2510808": "≤ 38,13%",
        }
    }

    # Tratamento especial para IN201
    # if sigla == "IN201":
    #     print(cidades)
        # if cidades and ano in metricas_in201 and cidades in metricas_in201[ano]:
        #     for cidade in cidades:
        #         meta = metricas_in201[ano][cidade]
        #         st.metric(label=f"Métrica - {sigla} ({ano}, IBGE: {ibge})", value=meta)
        # else:
        #     meta = "Meta não definida para o município selecionado"
        #st.metric(label=f"Métrica - {sigla} ({ano}, IBGE: {ibge})", value=meta)
    if sigla=='IN201':
        data_in201 = {
        "Sigla": ["IN201"] * 16,
        "Ano": [2023, 2024, 2023, 2024, 2023, 2024, 2023, 2024, 2023, 2024, 2023, 2024, 2023, 2024, 2023, 2024],
        "IBGE": [
            "2507507", "2507507", "2501153", "2501153", "2502300", "2502300", 
            "2503704", "2503704", "2504009", "2504009", "2504033", "2504033", 
            "2510600", "2510600", "2510808", "2510808"
        ],
        "Cidade": [
            "João Pessoa", "João Pessoa", "Areia de Baraúnas", "Areia de Baraúnas", "Bom Sucesso", "Bom Sucesso", 
            "Cajazeiras", "Cajazeiras", "Campina Grande", "Campina Grande", "Capim", "Capim", 
            "Ouro Velho", "Ouro Velho", "Patos", "Patos"
        ],
        "Valor_Meta": [
            "≤ 55,3%", "≤ 52,3%", "≤ 38,13%", "≤ 38,13%", "≤ 38,13%", "≤ 38,13%",
            "≤ 38,13%", "≤ 38,13%", "≤ 38,13%", "≤ 38,13%", "≤ 75,00%", "≤ 70,00%",
            "≤ 38,13%", "≤ 38,13%", "≤ 38,13%", "≤ 38,13%"
            ]
        }

        # Criar DataFrame
        df_in201 = pd.DataFrame(data_in201)
        df_in201 = df_in201[df_in201['Ano'] == ano]
        st.write(df_in201)
        meta = ''
    else:
    # Verificar se a sigla e o ano existem no dicionário
        if sigla in metricas_meta and ano in metricas_meta[sigla]:
            meta = metricas_meta[sigla][ano]
        else:
            meta = "Meta não definida"

    # Exibir métricas no Streamlit
    st.metric(label=" ", value=meta)
    #st.metric(label=f"Métrica - {sigla} ({ano})", value=meta)

    # Exemplo de diferentes valores para cada sigla
    # Adiciona uma métrica complementar
    switch_values = {
        "IN200": "Qualidade Máxima",
        "IN202": "Tratamento Eficiente",
        "IN203": "Cobertura Satisfatória",
        "IN204": "Sem meta definida",
        "IN205": "Hidrômetros Substituídos",
        "IN208": "Água de Qualidade"
    }
    descricao = switch_values.get(sigla, "Sem descrição disponível")

    # Exibir descrição complementar
    #st.write(f"**Descrição:** {descricao}")