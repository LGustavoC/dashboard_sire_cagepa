import pandas as pd
import geopandas as gpd
import streamlit as st
from utils.functions import clean_data

@st.cache_data
def load_data(indicators_path, glossary_path):
    """
    Carrega e mescla os dados dos indicadores e do glossário em um único DataFrame.
    """
    # Carregar arquivos
    indicators_data = pd.read_csv(indicators_path)
    glossary_data = pd.read_csv(glossary_path)

    # Mesclar dados pelo campo 'Sigla'
    consolidated_data = pd.merge(
        indicators_data,
        glossary_data[["Sigla", "Título", "Unidade"]],  # Selecionar colunas úteis
        on="Sigla",
        how="left"
    )

    return consolidated_data

def load_geojson(file_path):
    return gpd.read_file(file_path)

def load_indicator_data(file_path):
    data = pd.read_csv(file_path, sep=',')
    # Limpar dados
    columns_to_check = ["IBGE", "Cidade", "Sigla", "Ano", "Valor"]  # Colunas críticas
    data = clean_data(data, columns_to_check)
    

    data["Ano"] = data["Ano"].astype(str)
    data["IBGE"] = data["IBGE"].astype(str)

    # Tratar valores ausentes e garantir consistência
    data["Mês"] = data["Mês"].fillna("Indefinido")
    data["Ano"] = data["Ano"].fillna("Sem ano").astype(str)

    meses = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho",
        7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }
    data["Mês"] = data["Mês"].map(meses)
    
    return data
