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

def agrupar_dados_por_microrregiao(indicator_data, microrregioes, operacoes):
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
