from components.popups import create_popup_with_tabs, create_custom_popup_microrregiao, create_popup_with_tabs_microrregioes
import folium
from folium.plugins import Fullscreen

def create_map(geojson, data, municipios_selecionados, nao_atendidas):
    """
    Gera um mapa interativo com as cidades selecionadas e popups organizados em abas.
    """
    map_center = [-7.1212, -36.7246]
    mapa = folium.Map(location=map_center, zoom_start=8)

    Fullscreen(position="topright", title="Tela cheia", title_cancel="Sair da tela cheia").add_to(mapa)

    for _, row in geojson.iterrows():
        municipio = row["name"].upper()
        municipio_id = row["id"]

        # Verificar se a cidade está na lista de não atendidas
        if municipio_id in nao_atendidas:
            color = "gray"
            popup_info = f"<b>{municipio}</b><br>Não atendida."
        else:
            # Filtrar os dados para a cidade atual
            municipio_data = data[data["IBGE"] == municipio_id].copy()

            if not municipio_data.empty:  # Cidade com dados
                if municipio in municipios_selecionados:
                    color = "blue"
                    popup_info = create_popup_with_tabs(municipio_data, municipio)
                else:  # Cidade não selecionada (fora do filtro)
                    color = "gray"
                    popup_info = f"<b>{municipio}</b><br>Sem dados disponíveis (fora do filtro)."
            else:  # Cidade sem dados
                if municipio in municipios_selecionados:
                    color = "red"
                    popup_info = f"<b>{municipio}</b><br>Sem dados disponíveis."
                else:  # Cidade não selecionada
                    color = "gray"
                    popup_info = f"<b>{municipio}</b><br>Sem dados disponíveis (fora do filtro)."

        # Adicionar a cidade ao mapa
        folium.GeoJson(
            row.geometry,
            style_function=lambda x, col=color: {
                "fillColor": col,
                "color": "black",
                "weight": 1,
                "fillOpacity": 0.7,
            },
            tooltip=municipio,
            popup=folium.Popup(popup_info, max_width=1000),
        ).add_to(mapa)

    return mapa

def create_map_microrregioes(geojson, microrregiao_data, microrregioes, is_anual):
    """
    Cria um mapa com as cidades exibindo dados consolidados por microrregião.
    """
    mapa = folium.Map(location=[-7.1212, -36.7246], zoom_start=8)
    Fullscreen(position="topright").add_to(mapa)

    # Definir cores únicas para cada microrregião
    cores = ["red", "green", "orange", "blue", "purple", "yellow"]
    cor_microrregiao = {microrregiao: cores[i % len(cores)] for i, microrregiao in enumerate(microrregioes)}

    # Iterar sobre as cidades no GeoJSON
    for _, row in geojson.iterrows():
        municipio = row["name"]
        municipio_id = str(row["id"])

        # Identificar a microrregião da cidade
        microrregiao = next(
            (m for m, cidades in microrregioes.items() if municipio_id in cidades), None
        )

        if microrregiao:
            color = cor_microrregiao[microrregiao]

            # Filtrar os dados da microrregião
            dados_microrregiao = microrregiao_data[microrregiao_data["Microrregião"] == microrregiao].copy()
            
            # Atualizar a coluna "Mês" para "Indefinido" explicitamente usando `.loc`
            dados_microrregiao.loc[:, "Mês"] = "Indefinido"

            # Criar popup com os dados da microrregião
            popup_info = create_popup_with_tabs_microrregioes(dados_microrregiao, microrregiao, is_anual)

            # Adicionar a cidade ao mapa com o estilo da microrregião
            folium.GeoJson(
                row.geometry,
                style_function=lambda x, color=color: {
                    "fillColor": color,
                    "color": "black",
                    "weight": 1,
                    "fillOpacity": 0.5,
                },
                tooltip=folium.Tooltip(f"{municipio} ({microrregiao})"),
                popup=folium.Popup(popup_info, max_width=1000)
            ).add_to(mapa)

    return mapa