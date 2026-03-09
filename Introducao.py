import plotly.express as px
import pandas as pd

df = pd.read_csv('clientes-v3-preparado.csv')

# Gráfico de dispersão
fig = px.scatter(df, x='idade', y='salario', color='nivel_educacao', hover_data=['estado_civil'])
fig.update_layout(
    title='Idade vs Salário por Nível de Educação',
    xaxis_title='Idade',
    yaxis_title='Salário'

)
fig.write_html("meu_grafico.html")

