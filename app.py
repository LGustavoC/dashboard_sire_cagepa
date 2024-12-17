import streamlit as st
from components.map import create_map, create_map_microrregioes
from components.tables import show_detailed_table
from components.charts import create_comparative_chart_with_tabs, create_comparative_chart_with_tabs_microrregioes
from utils.data_loader import load_geojson, load_indicator_data
from utils.functions import dotRemove, agrupar_dados_por_microrregiao, changeMax
from streamlit_folium import st_folium
import pandas as pd

# Configuração do layout
st.set_page_config(page_title="Dashboard PS", page_icon=":bar_chart:", layout="wide")

# Adicionar o logo e título
st.image("./assets/logo.png", width=500)  # Substitua pelo caminho correto do logo
st.title("Dashboard de Indicadores - Prestação de Serviço")

# Estilos customizados
with open("./styles/custom.css") as css:
    st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)

# Carregar dados
geojson = load_geojson("./data/geojs-25-mun.json")
indicator_data = load_indicator_data("./data/sire_indicador_valor_grid.csv")
indicadores_desejados = ["IN200",
                         "IN201",
                         "IN202",
                         "IN203",
                         "IN204",
                         "IN205",
                         "IN208"]

municipios_obrigatorios_filtro = ['2507507',
                                  '2504009',
                                  '2503704',
                                  '2504033',
                                  '2510808',
                                  '2502300',
                                  '2501153',
                                  '2510600'
]
indicator_data = indicator_data[indicator_data["Sigla"].isin(indicadores_desejados)]
indicator_data["Ano"] = indicator_data["Ano"].apply(dotRemove)
#indicator_data["Valor"] = indicator_data["Valor"].apply(changeMax)
indicator_data = indicator_data[indicator_data["Ano"].isin(['2023', '2024'])]
#indicator_data = indicator_data[indicator_data["Valor"] != '.00']
indicator_data = indicator_data[indicator_data["IBGE"].isin(municipios_obrigatorios_filtro)]
# Converta a coluna 'salário' para o tipo numérico; definir valores não numéricos para NaN
indicator_data[ "Valor" ] = pd.to_numeric(indicator_data[ "Valor" ], errors= "coerce" ) 

# Descartar linhas contendo NaN na coluna 'salary'
indicator_data.dropna(subset=[ "Valor" ], inplace= True )

# Carregar glossário
glossario_data = pd.read_csv("./data/sire_indicador_grid.csv", sep=",")

general_indicator_value = pd.merge(
    indicator_data,
    glossario_data[["Sigla", "Título"]],  # Selecionar colunas úteis
    on="Sigla",
    how="left"
)

st.markdown("### Glossário de Indicadores")
glossario = general_indicator_value[["Sigla", "Título"]].drop_duplicates().sort_values("Sigla")

# Criar HTML da tabela sem índice
glossario_html = glossario.to_html(index=False, escape=False, classes="custom-table")

# Estilos personalizados
custom_css = """
<style>
.custom-table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
    font-size: 16px;
    text-align: left;
}
.custom-table th {
    background-color: #003893; /* Cor do cabeçalho */
    color: white;
    padding: 12px;
    text-align: center;
}
.custom-table td {
    border: 1px solid #ddd;
    padding: 8px;
    font-weight:600;
}
.custom-table tr:hover {
    background-color: #4eacfa; /* Efeito hover */
}
</style>
"""

# Exibir a tabela estilizada no Streamlit
st.markdown(custom_css + glossario_html, unsafe_allow_html=True)

# Configuração: IBGEs de cidades não atendidas
nao_atendidas = [""]  # Exemplo de IBGEs de cidades não atendidas

# Mapeamento de meses
meses_map = {1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho",
             7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}
meses_invert_map = {v: k for k, v in meses_map.items()}

# Lista de anos e meses disponíveis
#anos_disponiveis = sorted(indicator_data["Ano"].unique())
anos_disponiveis = ['2023', '2024']
meses_disponiveis = sorted(indicator_data["Mês"].dropna().unique(), key=lambda x: meses_invert_map[x])

# Criar abas para Cidade e Microrregiões
tabs = st.tabs(["Cidade", "Microrregiões"])

with tabs[0]:  # Aba de Cidades
    st.markdown("### Visualização por Cidade")

    # Filtros para cidades
    municipios = ["Todos"] + sorted(indicator_data["Cidade"].unique())
    municipios_selecionados = st.sidebar.multiselect("Selecione os Municípios", municipios, default="Todos")

    if "Todos" in municipios_selecionados:
        municipios_selecionados = indicator_data["Cidade"].unique().tolist()

    indicadores = ["Todos"] + sorted(indicator_data["Sigla"].unique())
    indicadores_selecionados = st.sidebar.multiselect("Selecione os Indicadores", indicadores, default="Todos")

    if "Todos" in indicadores_selecionados:
        indicadores_selecionados = indicator_data["Sigla"].unique().tolist()

    ano_inicial = st.sidebar.selectbox("Ano", anos_disponiveis, index=0)
    #ano_final = st.sidebar.selectbox("Ano Final", anos_disponiveis, index=len(anos_disponiveis) - 1)
    ano_final = ano_inicial
    mes_inicial = st.sidebar.selectbox("Mês Inicial", meses_disponiveis, index=0)
    mes_final = st.sidebar.selectbox("Mês Final", meses_disponiveis, index=len(meses_disponiveis) - 1)
    #is_anual = st.sidebar.checkbox("Consolidado Anual")
    is_anual = False

    # Filtrar os dados
    filtered_data_cidades = indicator_data[
        (indicator_data["Sigla"].isin(indicadores_selecionados)) &
        (indicator_data["Ano"] >= ano_inicial) & 
        (indicator_data["Ano"] <= ano_final) & 
        (indicator_data["Mês"].map(meses_invert_map) >= meses_invert_map[mes_inicial]) &
        (indicator_data["Mês"].map(meses_invert_map) <= meses_invert_map[mes_final]) & 
        (indicator_data["Cidade"].isin(municipios_selecionados))
    ]
    general_indicator_value = general_indicator_value[general_indicator_value["Ano"].isin([ano_inicial, ano_final])]
    # Exibir tabelas e mapa para cidades
    #show_consolidated_table(filtered_data_cidades, indicadores_selecionados, is_anual)
    #mapa_cidades = create_map(geojson, filtered_data_cidades, municipios_selecionados, nao_atendidas)
    #st_folium(mapa_cidades, width=1000, height=600)
    show_detailed_table(filtered_data_cidades, is_anual)
    create_comparative_chart_with_tabs(
        data=general_indicator_value,
        cidades=municipios_selecionados,
        indicadores=indicadores_selecionados,
        periodo_anual=is_anual,
        ano_selecionado=ano_inicial
    )

# Aba de Microrregiões
with tabs[1]:  # Aba de Microrregiões
    st.markdown("### Visualização por Microrregiões")
    # Definir microrregiões
    microrregioes = {
        "ALTO PIRANHAS": [
            "2500775", "2502003", "2502052", "2502201", "2502300", "2502409", 
            "2502805", "2502904", "2503308", "2503704", "2504108", "2504306", 
            "2507408", "2513653", "2508109", "2508406", "2509156", "2509370", 
            "2509602", "2510006", "2510907", "2512036", "2512077", "2512804", 
            "2513208", "2513307", "2513901", "2513968", "2513984", "2500700", 
            "2514206", "2514503", "2514651", "2516201", "2516805", "2516904", 
            "2517209", "2505501"
            ],
        "BORBOREMA": [
            "2500304", "2500403", "2500536", "2500577", "2500734", "2500908",
            "2501005", "2501203", "2501302", "2501351", "2501500", "2501534",
            "2501575", "2501609", "2501708", "2502151", "2502508", "2503100",
            "2503506", "2503555", "2503902", "2504009", "2504074", "2504157",
            "2504355", "2504702", "2504850", "2505006", "2505105", "2505352",
            "2505402", "2505709", "2506004", "2506103", "2506202", "2506251",
            "2506509", "2507705", "2507804", "2508307", "2508505", "2509206",
            "2509339", "2509396", "2509503", "2509701", "2509909", "2510105",
            "2510303", "2510501", "2510600", "2510659", "2511103", "2511400",
            "2512002", "2512200", "2512408", "2512507", "2512705", "2512747",
            "2512754", "2512788", "2513158", "2513851", "2513943", "2514008",
            "2514107", "2514800", "2515104", "2515203", "2515401", "2515500",
            "2515807", "2515906", "2516003", "2516102", "2516151", "2516300",
            "2516409", "2516508", "2516706", "2516755", "2517001", "2517407"
            ],
        "ESPINHARAS": [
            "2500106", "2500205", "2501153", "2502102", "2503407", "2503753",
            "2504207", "2504405", "2504504", "2504801", "2505303", "2505600",
            "2505907", "2506608", "2502607", "2506707", "2507002", "2508000",
            "2508703", "2508802", "2509008", "2510204", "2510402", "2510709",
            "2510808", "2511004", "2511301", "2512101", "2512309", "2512606",
            "2513000", "2513356", "2513406", "2513505", "2513604", "2513802",
            "2513927", "2514305", "2514404", "2514552", "2514602", "2514701",
            "2514909", "2515708", "2516607", "2517100", "2517100"
        ],
        "LITORAL": [
            "2500502", "2500601", "2500809", "2501104", "2501401", "2501807",
            "2501906", "2502706", "2503001", "2503209", "2503605", "2503803",
            "2504033", "2504603", "2504900", "2505238", "2505204", "2505279",
            "2505808", "2506301", "2506400", "2506806", "2506905", "2507101",
            "2507200", "2507309", "2507507", "2507606", "2507903", "2508208",
            "2508554", "2508604", "2508901", "2509057", "2509107", "2509305",
            "2509404", "2509800", "2511202", "2512721", "2511509", "2511608",
            "2511707", "2511806", "2511905", "2512762", "2512903", "2513109",
            "2513703", "2514453", "2515005", "2515302", "2515609", "2515930",
            "2515971"
        ]
    }

    # Definir operações por indicador
    operacoes = {
        "IN200": "mean",
        "IN201": "mean",
        "IN202": "mean",
        "IN203": "mean",
        "IN204": "mean",
        "IN205": "mean",
        "IN206": "mean",
        "IN207": "mean",
        "IN208": "mean",
        "IN209": "mean",
        "IN210": "mean",
        "IN211": "mean",
        "IN212": "mean",
        "IN213": "mean",
        "IN214": "mean",
        "IN215": "mean",
    }

    indicator_data = indicator_data[
        (indicator_data["Sigla"].isin(indicadores_selecionados)) &
        (indicator_data["Ano"] >= ano_inicial) & 
        (indicator_data["Ano"] <= ano_final) & 
        (indicator_data["Mês"].map(meses_invert_map) >= meses_invert_map[mes_inicial]) &
        (indicator_data["Mês"].map(meses_invert_map) <= meses_invert_map[mes_final])
    ]
    # Agrupar dados por microrregião
    microrregiao_data = agrupar_dados_por_microrregiao(indicator_data, microrregioes, operacoes)
    microrregiao_data["Valor"] = microrregiao_data["Valor"].apply(changeMax)
    # Adicionar seleção de microrregiões no sidebar
    microrregioes_disponiveis = ["Todas"] + list(microrregioes.keys())
    microrregioes_selecionadas = st.sidebar.multiselect(
        "Selecione as Microrregiões", microrregioes_disponiveis, default="Todas"
    )

    if "Todas" in microrregioes_selecionadas:
        cidades_microrregioes = sum(microrregioes.values(), [])
    else:
        cidades_microrregioes = sum(
            [microrregioes[m] for m in microrregioes_selecionadas if m in microrregioes],
            []
        )

    # Filtrar dados consolidados para microrregiões selecionadas
    if "Todas" in microrregioes_selecionadas:
        filtered_data_microrregioes = microrregiao_data  # Mantém todos os dados
    else:
        filtered_data_microrregioes = microrregiao_data[
            microrregiao_data["Microrregião"].isin(microrregioes_selecionadas)
        ]
    # Exibir tabela consolidada
    #show_consolidated_table(filtered_data_microrregioes, indicadores_selecionados, is_anual)

    # Criar mapa para microrregiões
    #mapa_microrregioes = create_map_microrregioes(geojson, filtered_data_microrregioes, microrregioes)
    #st_folium(mapa_microrregioes, width=1000, height=600)
    

    for microrregiao in microrregioes_selecionadas:
        if(microrregiao == 'Todas'):
            microrregioes_selecionadas = ['ALTO PIRANHAS',
                                        'BORBOREMA',
                                        'ESPINHARAS',
                                        'LITORAL']
            break

    filtered_data_microrregioes = pd.merge(
        filtered_data_microrregioes,
        glossario_data[["Sigla", "Título", "Unidade"]],  # Selecionar colunas úteis
        on="Sigla",
        how="left"
    )

    create_comparative_chart_with_tabs_microrregioes(
            filtered_data_microrregioes,
            microrregioes=microrregioes_selecionadas,
            indicadores=indicadores_selecionados,
            periodo_anual=is_anual,
            ano_selecionado=ano_inicial
        )
    #create_comparative_chart_with_tabs_microrregioes(filtered_data_microrregioes, microrregioes, general_indicator_value, is_anual)