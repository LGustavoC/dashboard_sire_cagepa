import folium

def create_popup_with_tabs(data, municipio):
    """
    Cria o conteúdo HTML do popup com abas de indicadores, organizando os dados por período e corrigindo estilo usando Bootstrap.
    """
    # Criar uma cópia explícita do DataFrame para evitar o aviso
    data = data.copy()

    # Ordenar os dados por Ano e Mês
    meses_ordenados = {
        "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4, "Maio": 5, "Junho": 6,
        "Julho": 7, "Agosto": 8, "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
    }
    data["Mês_Num"] = data["Mês"].map(meses_ordenados).fillna(0).astype(int)
    data = data.sort_values(by=["Ano", "Mês_Num"])

    indicadores = data["Sigla"].unique()
    html = f"<h4>{municipio}</h4>"
    html += '<div class="container-fluid" style="max-width: 800px;">'  # Aumentar a largura do container
    html += '<ul class="nav nav-tabs" id="myTab" role="tablist">'

    # Criação das abas
    for i, indicador in enumerate(indicadores):
        active = "active" if i == 0 else ""
        html += f"""
        <li class="nav-item" role="presentation">
            <button class="nav-link {active}" id="tab-{indicador}-tab" data-bs-toggle="tab" data-bs-target="#tab-{indicador}" type="button" role="tab" aria-controls="tab-{indicador}" aria-selected="{str(i == 0).lower()}">
                {indicador}
            </button>
        </li>
        """
    html += "</ul>"

    # Conteúdo das abas
    html += '<div class="tab-content" id="myTabContent" style="max-height: 400px; overflow-y: auto;">'
    for i, indicador in enumerate(indicadores):
        active = "show active" if i == 0 else ""
        tab_data = data[data["Sigla"] == indicador][["Ano", "Mês", "Valor"]].copy()  # Cópia explícita
        html += f"""
        <div class="tab-pane fade {active}" id="tab-{indicador}" role="tabpanel" aria-labelledby="tab-{indicador}-tab">
            <div class="table-responsive">
                {tab_data.to_html(index=False, classes="table table-hover custom-table", escape=False)}
            </div>
        </div>
        """
    html += "</div></div>"

    # Estilos Personalizados
    custom_styles = """
    <style>
        .custom-table th {
            background-color: #f2f2f2;
            font-weight: bold;
            text-align: left;
        }
        .custom-table td, .custom-table th {
            padding: 10px;
        }
        .custom-table tbody tr:hover {
            background-color: #e3f2fd; /* Azul claro ao passar o mouse */
        }
        .container-fluid {
            margin: 0 auto;
        }
    </style>
    """

    # Importar CSS e JS do Bootstrap
    bootstrap_includes = """
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-GLhlTQ8iRABdZLl6O3oVMWSktN1Hxj1qejCjt2lFRGzFgGksJ1M+GILy9NfAiBsF" crossorigin="anonymous">
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js" integrity="sha384-w76A8fYF1rQc/nI6OQSZqLZLu3RAqc2EhbYDXKt6m26iRQE+nOSO3tE2BxJ0HUsg" crossorigin="anonymous"></script>
    """

    return bootstrap_includes + custom_styles + html

def create_popup_with_tabs_microrregioes(data, microrregiao, is_anual):
    """
    Cria o conteúdo HTML do popup com abas de indicadores para microrregiões,
    organizando os dados por período e corrigindo estilo usando Bootstrap.
    """
    # Criar uma cópia explícita do DataFrame para evitar o aviso
    data = data.copy()
    if(is_anual):
        data["Mês_Num"] = data["Mês"]
        data = data.sort_values(by=["Ano", "Mês_Num"])
    else:
        # Ordenar os dados por Ano e Mês
        meses_ordenados = {
            "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4, "Maio": 5, "Junho": 6,
            "Julho": 7, "Agosto": 8, "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
        }
        data["Mês_Num"] = data["Mês"].map(meses_ordenados).fillna(0).astype(int)
        data = data.sort_values(by=["Ano", "Mês_Num"])

    indicadores = data["Sigla"].unique()
    html = f"<h4>{microrregiao}</h4>"
    html += '<div class="container-fluid" style="max-width: 800px;">'  # Aumentar a largura do container
    html += '<ul class="nav nav-tabs" id="myTab" role="tablist">'

    # Criação das abas
    for i, indicador in enumerate(indicadores):
        active = "active" if i == 0 else ""
        html += f"""
        <li class="nav-item" role="presentation">
            <button class="nav-link {active}" id="tab-{indicador}-tab" data-bs-toggle="tab" data-bs-target="#tab-{indicador}" type="button" role="tab" aria-controls="tab-{indicador}" aria-selected="{str(i == 0).lower()}">
                {indicador}
            </button>
        </li>
        """
    html += "</ul>"

    # Conteúdo das abas
    html += '<div class="tab-content" id="myTabContent" style="max-height: 400px; overflow-y: auto;">'
    for i, indicador in enumerate(indicadores):
        active = "show active" if i == 0 else ""
        tab_data = data[data["Sigla"] == indicador][["Ano", "Mês", "Valor"]].copy()  # Cópia explícita
        html += f"""
        <div class="tab-pane fade {active}" id="tab-{indicador}" role="tabpanel" aria-labelledby="tab-{indicador}-tab">
            <div class="table-responsive">
                {tab_data.to_html(index=False, classes="table table-hover custom-table", escape=False)}
            </div>
        </div>
        """
    html += "</div></div>"

    # Estilos Personalizados
    custom_styles = """
    <style>
        .custom-table th {
            background-color: #f2f2f2;
            font-weight: bold;
            text-align: left;
        }
        .custom-table td, .custom-table th {
            padding: 10px;
        }
        .custom-table tbody tr:hover {
            background-color: #e3f2fd; /* Azul claro ao passar o mouse */
        }
        .container-fluid {
            margin: 0 auto;
        }
    </style>
    """

    # Importar CSS e JS do Bootstrap
    bootstrap_includes = """
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-GLhlTQ8iRABdZLl6O3oVMWSktN1Hxj1qejCjt2lFRGzFgGksJ1M+GILy9NfAiBsF" crossorigin="anonymous">
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js" integrity="sha384-w76A8fYF1rQc/nI6OQSZqLZLu3RAqc2EhbYDXKt6m26iRQE+nOSO3tE2BxJ0HUsg" crossorigin="anonymous"></script>
    """

    return bootstrap_includes + custom_styles + html

def create_custom_popup_microrregiao(microrregiao, microrregiao_data):
    """
    Cria um HTML personalizado para o popup de uma cidade, com os dados da microrregião.
    """
    dados_microrregiao = microrregiao_data[microrregiao_data["Microrregião"] == microrregiao]

    # Início do HTML do popup
    popup_html = f"<h4>Microrregião: {microrregiao}</h4><table style='width: 100%; border: 1px solid black; border-collapse: collapse;'>"
    popup_html += "<tr><th style='border: 1px solid black; padding: 5px;'>Indicador</th><th style='border: 1px solid black; padding: 5px;'>Valor</th></tr>"

    # Adicionar cada indicador e seu valor na tabela
    for _, row in dados_microrregiao.iterrows():
        popup_html += f"<tr><td style='border: 1px solid black; padding: 5px;'>{row['Sigla']}</td>"
        popup_html += f"<td style='border: 1px solid black; padding: 5px;'>{row['Valor']}</td></tr>"

    # Finalizar o HTML
    popup_html += "</table>"

    return folium.Popup(popup_html, max_width=300)
