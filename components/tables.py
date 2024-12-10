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
    # Exibir tabela detalhada
    st.markdown("### Dados Detalhados por Município")
    if not data.empty:
        # Exibir apenas as colunas relevantes
        st.dataframe(data[["IBGE", "Cidade", "Sigla", "Valor", "Ano", "Mês"]], use_container_width=True)
    else:
        st.warning("Nenhum dado detalhado disponível para os filtros selecionados.")
