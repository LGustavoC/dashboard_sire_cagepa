import streamlit as st

def show_consolidated_table(data, indicadores, is_anual):
    """
    Exibe a tabela consolidada apenas para a Paraíba (IBGE = 25).
    """
    pb_data = data[data["IBGE"] == "25"]  # Filtrar dados para Paraíba (IBGE = 25)
    
    # Filtrar os dados com base nos indicadores e tipo (anual/mensal)
    if is_anual:
        filtered_data = pb_data[(pb_data["Sigla"].isin(indicadores)) & (pb_data["Mês"].isna())]
    else:
        filtered_data = pb_data[(pb_data["Sigla"].isin(indicadores))]

    # Exibir tabela consolidada
    st.markdown("### Dados Consolidados para Paraíba")
    if not filtered_data.empty:
        st.dataframe(filtered_data[["Sigla", "Valor", "Ano", "Mês"]], use_container_width=True)
    else:
        st.warning("Nenhum dado consolidado disponível para os filtros selecionados.")

def show_detailed_table(data, is_anual):
    """
    Exibe a tabela detalhada com base nos filtros aplicados.
    """
        # Mapeamento de meses para valores numéricos
    meses_ordenados = {
        "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4, "Maio": 5, "Junho": 6,
        "Julho": 7, "Agosto": 8, "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
    }
    data = data.copy()
    # Garantir que as colunas `Mês` e `Ano` estão preenchidas
    data["Mês"] = data["Mês"].fillna("Indefinido")
    data["Ano"] = data["Ano"].fillna("Indefinido")
    if is_anual:
        data = data[data['Mês']== 'Indefinido']
    else:
        # Criar colunas auxiliares `Mês_Num` e `Período`
        data["Mês_Num"] = data["Mês"].map(meses_ordenados).fillna(0).astype(int)
        data["Período"] = data["Mês"] + "/" + data["Ano"]
        # Garantir que `Período` seja válido
        data = data[~data["Período"].str.contains("Indefinido|Indefinido")]
        data = data.sort_values(['Sigla','Mês_Num','Ano','Cidade'])
    # Exibir tabela detalhada
    st.markdown("### Dados Detalhados por Município")
    if not data.empty:
        # Exibir apenas as colunas relevantes
        st.dataframe(data[["Sigla","Mês", "Ano","IBGE","Cidade","Valor"]], use_container_width=True)
    else:
        st.warning("Nenhum dado detalhado disponível para os filtros selecionados.")
