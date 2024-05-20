import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import random
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error


# Função para gerar uma base de dados fictícia
def gerar_base_dados():
    base_dados = {
        "Magazine Luiza": {"visitas": [], "vendas": []},
        "Casas Bahia": {"visitas": [], "vendas": []},
        "Americanas": {"visitas": [], "vendas": []}
    }
    # Gerar dados para os últimos 30 dias
    data_atual = datetime.now()
    for i in range(30):
        data = data_atual - timedelta(days=i)
        for marketplace, dados in base_dados.items():
            visitas = random.randint(1000, 5000)
            vendas = random.randint(50, 200)
            # Adicionando o campo 'numero_paginas'
            numero_paginas = random.randint(1, 10)
            dados["visitas"].append({"data": data.strftime("%Y-%m-%d"), "valor": visitas, "tempo": random.uniform(1, 10), "numero_paginas": numero_paginas})
            dados["vendas"].append({"data": data.strftime("%Y-%m-%d"), "valor": vendas})
    return base_dados

# Gerar a base de dados com 3 marketplaces
base_dados = gerar_base_dados()

# Extrair features e target dos dados
X = []
y = []
for marketplace, data in base_dados.items():
    for i in range(len(data['vendas'])):
        visitas = data['visitas'][i]['valor']
        vendas = data['vendas'][i]['valor']
        X.append([visitas])
        y.append(vendas)

# Dividir os dados em conjuntos de treino e teste
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Treinar o modelo de regressão linear
regression_model = LinearRegression()
regression_model.fit(X_train, y_train)

# Avaliar o modelo
y_pred = regression_model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
print("Mean Squared Error:", mse)


# Inicialização do aplicativo Dash
app = dash.Dash(__name__)


# Função para calcular o Tempo Médio na Página
def calcular_tempo_medio_pagina(visitas_data):
    total_visitas = len(visitas_data)
    tempo_total = sum(visita['tempo'] for visita in visitas_data)
    return tempo_total / total_visitas if total_visitas != 0 else 0

# Função para calcular a Taxa de Conversão de Vendas
# Função para calcular a Taxa de Conversão de Vendas
def calcular_taxa_conversao(vendas_data, visitas_data, taxa_rejeicao):
    total_visitas = len(visitas_data)
    total_vendas = sum(data['valor'] for data in vendas_data)
    if total_visitas != 0:
        taxa_conversao = (total_vendas / total_visitas) * 100
        # Ajustar a taxa de conversão subtraindo a taxa de rejeição e garantindo que seja entre 0 e 100
        taxa_conversao = min(max(taxa_conversao - taxa_rejeicao, 0), 100)
        return taxa_conversao
    else:
        return 0




# Função para calcular a Taxa de Rejeição
def calcular_taxa_rejeicao(visitas_data):
    total_visitas = len(visitas_data)
    visitas_uma_pagina = sum(1 for visita in visitas_data if visita['numero_paginas'] == 1)
    return (visitas_uma_pagina / total_visitas) * 100 if total_visitas != 0 else 0





# Layout do dashboard
app.layout = html.Div(children=[
    html.H1(children='Dashboard de Marketplaces', style={'textAlign': 'center', 'marginBottom': '20px', 'color': '#333', 'fontFamily': 'Arial, sans-serif'}),

    html.Div(id='relatorio', style={'textAlign': 'center', 'fontSize': '20px', 'marginBottom': '20px'}),

    html.Div(children='''
        Dados de Tráfego e KPIs
    ''', style={'textAlign': 'center', 'fontSize': '20px', 'color': '#666', 'fontFamily': 'Arial, sans-serif'}),

    dcc.Graph(
        id='vendas-stats',
        style={'width': '80%', 'margin': 'auto', 'marginTop': '20px'}
    ),

    dcc.Graph(
        id='visitas-gerais',
        style={'width': '80%', 'margin': 'auto', 'marginTop': '20px'}
    ),

    html.Div(id='marketplace-stats-container', children=[
        dcc.Dropdown(
            id='marketplace-dropdown',
            options=[{'label': mp, 'value': mp} for mp in base_dados.keys()],
            value=list(base_dados.keys())[0]
        ),

        html.Div(style={'margin-top': '20px'}),  # Espaçamento entre o dropdown e o kpi-container

        html.Div(id='kpi-container', children=[
            html.Div(id='tempo-medio-pagina', style={'textAlign': 'center', 'fontSize': '24px', 'fontWeight': 'bold', 'border': '2px solid #666', 'display': 'inline-block', 'padding': '10px', 'marginRight': '10px'}),
            html.Div(id='taxa-conversao', style={'textAlign': 'center', 'fontSize': '24px', 'fontWeight': 'bold', 'border': '2px solid #666', 'display': 'inline-block', 'padding': '10px', 'marginRight': '10px'}),
            html.Div(id='taxa-rejeicao', style={'textAlign': 'center', 'fontSize': '24px', 'fontWeight': 'bold', 'border': '2px solid #666', 'display': 'inline-block', 'padding': '10px'})
        ]),

        html.Div(style={'margin-top': '20px'}),  # Espaçamento entre o kpi-container e os gráficos

        dcc.Graph(
            id='marketplace-visitas',
            style={'width': '80%', 'margin': 'auto', 'marginTop': '20px'},
        ),

        dcc.Graph(
            id='marketplace-vendas',
            style={'width': '80%', 'margin': 'auto', 'marginTop': '20px'},
        ),

        dcc.Graph(
            id='previsao-vendas',
            style={'width': '80%', 'margin': 'auto', 'marginTop': '20px'}
        )
    ])
])


# Callback para atualizar o gráfico geral de visitas
@app.callback(
    Output('visitas-gerais', 'figure'),
    [Input('marketplace-dropdown', 'value')]
)
def update_overall_visitas(selected_marketplace):
    visitas_totais = [sum(data['valor'] for data in base_dados[mp]['visitas']) for mp in base_dados.keys()]
    fig = go.Figure(go.Bar(x=list(base_dados.keys()), y=visitas_totais))
    fig.update_layout(title='Total de Visitas Geral', xaxis_title='Marketplace', yaxis_title='Total de Visitas')
    return fig


# Callback para atualizar os gráficos de vendas e visitas por marketplace
@app.callback(
    [Output('marketplace-visitas', 'figure'),
     Output('marketplace-vendas', 'figure'),
     Output('vendas-stats', 'figure')],
    [Input('marketplace-dropdown', 'value')]
)
def update_marketplace_graphs(selected_marketplace):
    visitas_data = base_dados[selected_marketplace]["visitas"]
    vendas_data = base_dados[selected_marketplace]["vendas"]

    visitas_fig = go.Figure(go.Scatter(x=[data["data"] for data in visitas_data], y=[data["valor"] for data in visitas_data], mode='lines+markers', name=f'Visitas - {selected_marketplace}'))
    visitas_fig.update_layout(
        title=f'Total de Visitas por Dia - {selected_marketplace}',
        xaxis_title='Data',
        yaxis_title='Visitas'
    )

    vendas_fig = go.Figure(go.Scatter(x=[data["data"] for data in vendas_data], y=[data["valor"] for data in vendas_data], mode='lines+markers', name=f'Vendas - {selected_marketplace}'))
    vendas_fig.update_layout(
        title=f'Total de Vendas por Dia - {selected_marketplace}',
        xaxis_title='Data',
        yaxis_title='Vendas'
    )

    vendas_overall_fig = go.Figure()

    for marketplace in base_dados.keys():
        vendas_total = [data["valor"] for data in base_dados[marketplace]["vendas"]]
        vendas_overall_fig.add_trace(go.Scatter(x=list(range(1, len(vendas_total) + 1)), y=vendas_total, mode='lines', name=f'Vendas - {marketplace}'))

    vendas_overall_fig.update_layout(
        title='Total de Vendas por Dia - Geral',
        xaxis_title='Dia',
        yaxis_title='Quantidade'
    )

    return visitas_fig, vendas_fig, vendas_overall_fig


## Callback para atualizar o relatório
@app.callback(
    Output('relatorio', 'children'),
    [Input('marketplace-dropdown', 'value')]
)
def update_report(selected_marketplace):
    visitas_data = base_dados[selected_marketplace]["visitas"]
    vendas_data = base_dados[selected_marketplace]["vendas"]

    # Calcular o ranking de vendas
    ranking_vendas = sorted(base_dados.keys(), key=lambda mp: sum(data["valor"] for data in base_dados[mp]["vendas"]), reverse=True)
    # Calcular o ranking de visitas
    ranking_visitas = sorted(base_dados.keys(), key=lambda mp: sum(data["valor"] for data in base_dados[mp]["visitas"]), reverse=True)

    # Adicionar números e bolinhas aos rankings
    ranking_vendas_com_bolinhas = [f'{i+1}º: {mp}' for i, mp in enumerate(ranking_vendas)]
    ranking_visitas_com_bolinhas = [f'{i+1}º: {mp}' for i, mp in enumerate(ranking_visitas)]

    return html.Div([
        html.H2('Relatório do Marketplace', style={'color': 'navy', 'textAlign': 'left'}),
        html.Div([
            html.P(f'Ranking de Vendas:', style={'fontSize': '18px', 'textAlign': 'left'}),
            html.Ul([html.Li(f'• {mp}') for mp in ranking_vendas_com_bolinhas], style={'list-style-type': 'none'})
        ], style={'textAlign': 'left'}),
        html.Div([
            html.P(f'Ranking de Visitas:', style={'fontSize': '18px', 'textAlign': 'left'}),
            html.Ul([html.Li(f'• {mp}') for mp in ranking_visitas_com_bolinhas], style={'list-style-type': 'none'})
        ], style={'textAlign': 'left'})
    ])

# Callback para atualizar os KPIs
# Callback para atualizar os KPIs
@app.callback(
    [Output('tempo-medio-pagina', 'children'),
     Output('taxa-conversao', 'children'),
     Output('taxa-rejeicao', 'children')],
    [Input('marketplace-dropdown', 'value')]
)
def update_kpis(selected_marketplace):
    visitas_data = base_dados[selected_marketplace]["visitas"]
    vendas_data = base_dados[selected_marketplace]["vendas"]
    
    # Calcula a taxa de rejeição
    taxa_rejeicao = calcular_taxa_rejeicao(visitas_data)

    # Calcular Tempo Médio na Página
    tempo_medio_pagina = calcular_tempo_medio_pagina(visitas_data)

    # Calcular Taxa de Conversão
    taxa_conversao = calcular_taxa_conversao(vendas_data, visitas_data, taxa_rejeicao)

    return f'Tempo Médio na Página: {tempo_medio_pagina:.2f} minutos', f'Taxa de Conversão: {taxa_conversao:.2f}%', f'Taxa de Rejeição: {taxa_rejeicao:.2f}%'


@app.callback(
    Output('previsao-vendas', 'figure'),
    [Input('marketplace-dropdown', 'value')]
)
def update_sales_prediction(selected_marketplace):
    visitas_data = base_dados[selected_marketplace]["visitas"]
    vendas_data = base_dados[selected_marketplace]["vendas"]

    visitas = [data["valor"] for data in visitas_data]
    vendas = [data["valor"] for data in vendas_data]

    # Gerar features para previsão
    features = [[visitas[i]] for i in range(len(visitas))]

    # Gerar previsões de vendas futuras
    sales_predictions = regression_model.predict(features)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[data["data"] for data in vendas_data], y=vendas, mode='lines+markers', name='Vendas Históricas'))
    fig.add_trace(go.Scatter(x=[data["data"] for data in vendas_data], y=sales_predictions, mode='lines', name='Previsão de Vendas'))

    fig.update_layout(
        title=f'Previsão de Vendas - {selected_marketplace}',
        xaxis_title='Data',
        yaxis_title='Vendas'
    )

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)


