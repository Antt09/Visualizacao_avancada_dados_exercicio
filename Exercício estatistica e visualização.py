import pandas as pd
import dash
import plotly.express as px
from dash import dcc, html, Input, Output

df_bruto = pd.read_csv('ecommerce_estatistica.csv')

# Preparação dos dados
df_bruto['Qtd_Vendidos'] = pd.to_numeric(df_bruto['Qtd_Vendidos'], errors='coerce')
generos_validos = df_bruto['Gênero'].value_counts().nlargest(5).index
marcas_frequentes = df_bruto['Marca'].value_counts().nlargest(10).index
df_semi = df_bruto[df_bruto['Gênero'].isin(generos_validos)].copy()
df = df_semi[df_semi['Marca'].isin(marcas_frequentes)].copy()
print(f"Total de linhas após filtros: {len(df)}")
print(df[['Marca', 'Gênero', 'Qtd_Vendidos', 'Preço']].head())

# Instanciação e layout do app
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1('Análise de Elasticidade de Preço por Marca', style={'textAlign': 'center'}),

    html.Div([
        html.Label("Selecione a Marca:"),
        dcc.Dropdown(
            id='filtro-marca',
            options=[{'label': m, 'value': m} for m in marcas_frequentes],
            value=marcas_frequentes[0],
            clearable=False
        ),
    ], style={'width': '40%', 'margin': 'auto', 'padding': '20px'}),

    dcc.Graph(id='grafico-regressao')
])

# Callback
@app.callback(
    Output('grafico-regressao', 'figure'),
    Input('filtro-marca', 'value')
)
def atualizar_grafico(marca_selecionada):
    dff = df[df['Marca'] == marca_selecionada]

    fig = px.scatter(
        dff,
        x='Preço',
        y='Qtd_Vendidos',
        color='Gênero',
        trendline='ols',
        title=f'Tendência de Vendas para a Marca: {marca_selecionada}',
        labels={'Qtd_Vendidos': 'Quantidade vendida', 'Preço': 'Preço (R$)'},
        template='plotly_white',
    )

    return fig

# Execução
if __name__ == '__main__':
    app.run(debug=True)

