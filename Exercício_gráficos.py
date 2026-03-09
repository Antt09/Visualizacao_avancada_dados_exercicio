import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px

# Limpeza bruta dos dados
try:
    df_bruto = pd.read_csv('ecommerce_estatistica.csv')
except FileNotFoundError:
    df_bruto = pd.DataFrame({
        'Material': ['algodão', 'poliéster', 'jean', 'jeans', 'brim 100% algodão', 'microfibra'],
        'Temporada': ['verão', 'inverno', '2021', 'verão', 'inverno', 'primavera-verão'],
        'Qtd_Vendidos': [100, 150, 80, 200, 50, 120],
        'Preço': [50.0, 60.0, 70.0, 80.0, 250.0, 45.0],
        'Nota': [4.5, 3.8, 4.0, 4.2, 4.7, 4.1]
    })

# Tratamento de nulos
df_bruto['Qtd_Vendidos'] = pd.to_numeric(df_bruto['Qtd_Vendidos'], errors='coerce').fillna(0)
df_bruto['Preço'] = pd.to_numeric(df_bruto['Preço'], errors='coerce').fillna(0)
df_bruto['Nota'] = pd.to_numeric(df_bruto['Nota'], errors='coerce').fillna(0)

# Limpeza inicial
df = df_bruto.dropna(subset=['Temporada', 'Material']).copy()
df['Temporada'] = df['Temporada'].str.strip().str.lower()
df['Material'] = df['Material'].str.strip().str.lower()

# Unificação de materiais
unificacao_material = {
    'jean': 'jeans',
    'brim 100% algodão': 'algodão',
    'brim': 'algodão',
    'poliester': 'poliéster'
}
df['Material'] = df['Material'].replace(unificacao_material)

# Unificação de temporadas
unificacao_temp = {
    'primavera-verão - outono-inverno': 'mista (todas)',
    'primavera-verão outono-inverno': 'mista (todas)',
    'primavera/verão/outono/inverno': 'mista (todas)',
    'primavera-verão': 'primavera/verão',
    'outono-inverno': 'outono/inverno',
    'verao': 'verão',
    '2021': 'mista (todas)'
}
df['Temporada'] = df['Temporada'].replace(unificacao_temp)
df = df[~df['Temporada'].isin(['não definido', 'n/a'])]

top_5_nomes = df['Material'].value_counts().nlargest(5).index.tolist()
df = df[df['Material'].isin(top_5_nomes)]

materiais_comuns = sorted(df['Material'].unique().tolist())
temporadas_unicas = sorted(df['Temporada'].unique().tolist())

# Função para os gráficos
def gerar_figuras(df_input):
    if df_input.empty:
        fig_vazia = px.scatter(title="Nenhum dado encontrado")
        fig_vazia.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)')
        return fig_vazia, fig_vazia, fig_vazia, fig_vazia, fig_vazia

    # Volume de Vendas
    fig1 = px.bar(
        df_input, x='Temporada', y='Qtd_Vendidos', color='Material',
        barmode='group', title='Volume de Vendas por Temporada', template='plotly_dark'
    )

    # Distribuição de Preços
    fig2 = px.box(
        df_input, x='Material', y='Preço', color='Material',
        title='Distribuição de Preços por Material', template='plotly_dark'
    )

    # Frequência de Preços
    fig3 = px.histogram(
        df_input, x='Preço', nbins=20, title='Frequência de Faixas de Preço',
        color_discrete_sequence=['#00d4ff'], template='plotly_dark'
    )

    # Relação Preço x Nota (com proteção de tamanho)
    fig4 = px.scatter(
        df_input, x='Preço', y='Nota', color='Material',
        size=df_input['Qtd_Vendidos'].clip(lower=1),
        title='Relação: Preço vs Avaliação (Nota)',
        template='plotly_dark', hover_data=['Temporada']
    )

    # Proporção de Vendas
    fig5 = px.pie(
        df_input, values='Qtd_Vendidos', names='Material',
        title='Proporção de Vendas por Material', template='plotly_dark'
    )

    # Transparência do fundo
    for f in [fig1, fig2, fig3, fig4, fig5]:
        f.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

    return fig1, fig2, fig3, fig4, fig5

# Layout do app
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Dashboard de Análise de E-commerce", style={'textAlign': 'center', 'padding': '20px', 'color': '#00d4ff'}),

    html.Div([
        html.Div([
            html.Label("Selecione os materiais (Unificados):", style={'color': '#ccc'}),
            dcc.Dropdown(
                id='dropdown-material',
                options=[{'label': m.capitalize(), 'value': m} for m in materiais_comuns],
                value=materiais_comuns,
                multi=True,
                style={'color': '#333'}
            ),
        ], style={'width': '45%', 'display': 'inline-block', 'marginRight': '5%'}),

        html.Div([
            html.Label("Selecione as Temporadas:", style={'color': '#ccc'}),
            dcc.Dropdown(
                id='checklist-temporada',
                options=[{'label': i.capitalize(), 'value': i} for i in temporadas_unicas],
                value=temporadas_unicas,
                multi=True,
                style={'color': '#333'}
            ),
        ], style={'width': '45%', 'display': 'inline-block'}),
    ], style={'padding': '30px', 'backgroundColor': '#1e1e26', 'borderRadius': '10px', 'margin': '20px'}),

    # Gráficos
    html.Div([
        html.Div([dcc.Graph(id='grafico-vendas')], style={'width': '50%', 'display': 'inline-block'}),
        html.Div([dcc.Graph(id='grafico-box-precos')], style={'width': '50%', 'display': 'inline-block'}),

        html.Div([dcc.Graph(id='grafico-hist-precos')], style={'width': '50%', 'display': 'inline-block'}),
        html.Div([dcc.Graph(id='grafico-scatter-nota')], style={'width': '50%', 'display': 'inline-block'}),

        html.Div([dcc.Graph(id='grafico-pizza-vendas')], style={'width': '100%', 'display': 'block'}),
    ], style={'padding': '20px'})
], style={'backgroundColor': '#111', 'minHeight': '100vh', 'color': 'white', 'fontFamily': 'Arial'})

# Callback
@app.callback(
    [Output('grafico-vendas', 'figure'),
     Output('grafico-box-precos', 'figure'),
     Output('grafico-hist-precos', 'figure'),
     Output('grafico-scatter-nota', 'figure'),
     Output('grafico-pizza-vendas', 'figure')],
    [Input('dropdown-material', 'value'),
     Input('checklist-temporada', 'value')]
)
def atualizacao_dash(materiais_sel, temporadas_sel):
    if not materiais_sel or not temporadas_sel:
        fig_vazia = px.scatter(title="Selecione filtros")
        fig_vazia.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)')
        return fig_vazia, fig_vazia, fig_vazia, fig_vazia, fig_vazia

    try:
        dff = df[
            (df['Material'].isin(materiais_sel)) &
            (df['Temporada'].isin(temporadas_sel))
        ]
        return gerar_figuras(dff)
    except Exception as e:
        print(f"Erro: {e}")
        error_fig = px.scatter(title="Erro ao carregar dados")
        error_fig.update_layout(template='plotly_dark')
        return error_fig, error_fig, error_fig, error_fig, error_fig

if __name__ == '__main__':
    app.run(debug=True)
