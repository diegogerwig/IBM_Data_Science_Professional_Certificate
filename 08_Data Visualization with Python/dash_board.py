# Dashboard de análisis de ventas de automóviles

import dash
from dash import dcc, html, Input, Output, callback
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import urllib.request
import io

# URL del archivo CSV
url = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/historical_automobile_sales.csv"

# Función para cargar los datos
def load_data():
    try:
        print("Descargando datos...")
        response = urllib.request.urlopen(url)
        data = response.read()
        text = io.BytesIO(data)
        df = pd.read_csv(text)
        print("Datos cargados correctamente.")
        return df
    except Exception as e:
        print(f"Error al descargar o cargar los datos: {e}")
        print("Creando datos de muestra...")
        
        # Código para generar datos sintéticos
        years = range(1980, 2023)
        months = range(1, 13)
        vehicle_types = ["Superminicar", "Smallfamilycar", "Mediumfamilycar", "Executivecar", "Sports"]
        recession_years = [1980, 1981, 1982, 1991, 2000, 2001, 2007, 2008, 2009, 2020]
        
        data = []
        for year in years:
            for month in range(1, 13):
                for vtype in vehicle_types:
                    is_recession = year in recession_years
                    
                    # Calcular ventas base
                    base_sales = 200 + (year - 1980) * 5
                    
                    # Aplicar factores
                    sales = base_sales * (0.7 if is_recession else 1.0)
                    sales *= 1.2 if vtype == "Superminicar" else 1.0
                    sales *= 0.9 if vtype == "Executivecar" and is_recession else 1.0
                    
                    # Añadir estacionalidad
                    sales *= 1.2 if month in [3, 4, 5] else 1.0  # Más ventas en primavera
                    
                    # Añadir ruido aleatorio
                    sales += np.random.normal(0, 20)
                    
                    # Añadir a los datos
                    data.append({
                        "Year": year,
                        "Month": month,
                        "Automobile_Sales": max(100, sales),
                        "Recession": 1 if is_recession else 0,
                        "Vehicle_Type": vtype,
                        "Price": np.random.randint(10000, 50000),
                        "Advertising_Expenditure": np.random.randint(1000, 10000),
                        "Consumer_Confidence": np.random.uniform(50, 100),
                        "Unemployment_Rate": np.random.uniform(3, 10) if not is_recession else np.random.uniform(7, 15),
                        "GDP": np.random.randint(10000, 30000),
                    })
        
        return pd.DataFrame(data)

# Cargar los datos
df = load_data()

# Inicializar la aplicación Dash
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server  # Para despliegue

# Definir el layout del dashboard
app.layout = html.Div([
    # Título del dashboard
    html.Div([
        html.H1("Dashboard de Análisis de Ventas de Automóviles", 
                style={
                    'textAlign': 'center',
                    'color': 'white',
                    'backgroundColor': '#2a3f5f',
                    'padding': '20px',
                    'marginBottom': '20px',
                    'borderRadius': '5px'
                }),
        html.H3("Análisis del impacto de recesiones económicas en las ventas de automóviles",
                style={
                    'textAlign': 'center',
                    'color': '#7FDBFF',
                    'backgroundColor': '#2a3f5f',
                    'padding': '10px',
                    'marginTop': '-20px',
                    'marginBottom': '20px',
                    'borderRadius': '0px 0px 5px 5px'
                })
    ]),
    
    # Controles de selección (dropdowns)
    html.Div([
        html.Div([
            # Menú para seleccionar tipo de reporte
            html.Div([
                html.H4('Seleccione el tipo de reporte:', style={'margin-bottom': '10px'}),
                dcc.Dropdown(
                    id='report-type',
                    options=[
                        {'label': 'Reporte de Recesión', 'value': 'recession'},
                        {'label': 'Reporte Anual', 'value': 'yearly'},
                        {'label': 'Reporte por Tipo de Vehículo', 'value': 'vehicle'}
                    ],
                    value='recession',  # Valor predeterminado
                    style={'width': '100%'}
                )
            ], style={'width': '30%', 'display': 'inline-block', 'margin-right': '2%'}),
            
            # Menú para seleccionar estadísticas
            html.Div([
                html.H4('Seleccione estadísticas:', style={'margin-bottom': '10px'}),
                dcc.Dropdown(
                    id='statistics-type',
                    options=[
                        {'label': 'Ventas por recesión', 'value': 'sales_recession'},
                        {'label': 'Ventas por tipo de vehículo', 'value': 'sales_vehicle'},
                        {'label': 'Gasto en publicidad', 'value': 'advertising'},
                        {'label': 'Relación precio-ventas', 'value': 'price_sales'},
                        {'label': 'Impacto de desempleo', 'value': 'unemployment'}
                    ],
                    value='sales_recession',  # Valor predeterminado
                    style={'width': '100%'}
                )
            ], style={'width': '30%', 'display': 'inline-block', 'margin-right': '2%'}),
            
            # Control para seleccionar rango de años
            html.Div([
                html.H4('Seleccione rango de años:', style={'margin-bottom': '10px'}),
                dcc.RangeSlider(
                    id='year-range',
                    min=1980,
                    max=2022,
                    step=1,
                    marks={
                        1980: '1980',
                        1990: '1990',
                        2000: '2000',
                        2010: '2010',
                        2020: '2020'
                    },
                    value=[1980, 2022],  # Valor predeterminado
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            ], style={'width': '33%', 'display': 'inline-block'})
        ], style={'padding': '20px', 'backgroundColor': 'white', 'borderRadius': '5px', 'margin-bottom': '20px'})
    ], style={'padding': '10px'}),
    
    # División para controles adicionales (se muestra/oculta según selección)
    html.Div(
        id='input-container',
        className='input-container',
        style={
            'backgroundColor': 'white', 
            'padding': '20px', 
            'borderRadius': '5px', 
            'margin': '10px',
            'minHeight': '100px',
            'display': 'none'  # Inicialmente oculto
        }
    ),
    
    # División para gráficos y resultados
    html.Div(
        id='output-container',
        className='output-container',
        children=[
            html.H3('Seleccione opciones arriba para visualizar datos', 
                   style={'textAlign': 'center', 'color': '#666', 'padding': '50px'})
        ],
        style={
            'backgroundColor': 'white', 
            'padding': '20px', 
            'borderRadius': '5px', 
            'margin': '10px',
            'boxShadow': '0px 0px 10px rgba(0,0,0,0.1)',
            'minHeight': '500px'
        }
    )
], style={'fontFamily': 'Arial, Helvetica, sans-serif', 'margin': '0px', 'padding': '0px', 'backgroundColor': '#F7F7F7'})

# Callbacks para la interactividad

# 1. Callback para actualizar el contenedor de entrada según el tipo de reporte
@app.callback(
    [Output('input-container', 'children'),
     Output('input-container', 'style')],
    [Input('report-type', 'value')]
)
def update_input_container(report_type):
    style = {
        'backgroundColor': 'white', 
        'padding': '20px', 
        'borderRadius': '5px', 
        'margin': '10px',
        'minHeight': '100px'
    }
    
    if report_type == 'recession':
        children = [
            html.H4('Seleccione periodo de recesión:', style={'margin-bottom': '10px'}),
            dcc.Dropdown(
                id='recession-period',
                options=[
                    {'label': 'Recesión 1980', 'value': '1980'},
                    {'label': 'Recesión 1981-1982', 'value': '1981-1982'},
                    {'label': 'Recesión 1991', 'value': '1991'},
                    {'label': 'Recesión 2000-2001', 'value': '2000-2001'},
                    {'label': 'Recesión 2007-2009', 'value': '2007-2009'},
                    {'label': 'Recesión 2020 (COVID-19)', 'value': '2020'},
                    {'label': 'Todas las recesiones', 'value': 'all'}
                ],
                value='all',
                style={'width': '50%'}
            )
        ]
        style['display'] = 'block'
    
    elif report_type == 'yearly':
        children = [
            html.H4('Seleccione año para análisis detallado:', style={'margin-bottom': '10px'}),
            dcc.Dropdown(
                id='specific-year',
                options=[{'label': str(year), 'value': year} for year in sorted(df['Year'].unique())],
                value=df['Year'].max(),
                style={'width': '50%'}
            )
        ]
        style['display'] = 'block'
    
    elif report_type == 'vehicle':
        children = [
            html.H4('Seleccione tipos de vehículos:', style={'margin-bottom': '10px'}),
            dcc.Checklist(
                id='vehicle-types',
                options=[{'label': vtype, 'value': vtype} for vtype in sorted(df['Vehicle_Type'].unique())],
                value=sorted(df['Vehicle_Type'].unique()),
                inline=True,
                style={'columnCount': 3}
            )
        ]
        style['display'] = 'block'
    
    else:
        children = []
        style['display'] = 'none'
    
    return children, style

# 2. Callback para actualizar el contenedor de salida basado en las selecciones
@app.callback(
    Output('output-container', 'children'),
    [Input('report-type', 'value'),
     Input('statistics-type', 'value'),
     Input('year-range', 'value')]
)
def update_output_container(report_type, statistics_type, year_range):
    # Filtrar datos por rango de años
    filtered_df = df[(df['Year'] >= year_range[0]) & (df['Year'] <= year_range[1])]
    
    # Título del reporte
    title = html.H2(f"Reporte de {report_type_to_text(report_type)}: {statistics_type_to_text(statistics_type)}",
                   style={'textAlign': 'center', 'color': '#2a3f5f', 'marginBottom': '20px'})
    
    # Generar gráficos según el tipo de reporte y estadísticas
    if report_type == 'recession' and statistics_type == 'sales_recession':
        # Ejemplo: Gráfico de ventas durante recesión vs no recesión
        rec_data = filtered_df[filtered_df['Recession'] == 1]
        non_rec_data = filtered_df[filtered_df['Recession'] == 0]
        
        rec_sales = rec_data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        non_rec_sales = non_rec_data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=rec_sales['Year'], y=rec_sales['Automobile_Sales'],
                                 mode='lines+markers', name='Recesión'))
        fig1.add_trace(go.Scatter(x=non_rec_sales['Year'], y=non_rec_sales['Automobile_Sales'],
                                 mode='lines+markers', name='No Recesión'))
        fig1.update_layout(title='Ventas de automóviles durante períodos de recesión vs no recesión',
                          xaxis_title='Año', yaxis_title='Ventas promedio')
        
        graph1 = dcc.Graph(figure=fig1)
        
        # Gráfico secundario 1: Ventas por tipo de vehículo durante recesiones
        vehicle_sales = rec_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        fig2 = px.bar(vehicle_sales, x='Vehicle_Type', y='Automobile_Sales',
                     title='Ventas promedio por tipo de vehículo durante recesiones')
        graph2 = dcc.Graph(figure=fig2)
        
        # Gráfico secundario 2: PIB vs Ventas durante recesiones
        fig3 = px.scatter(rec_data, x='GDP', y='Automobile_Sales', color='Vehicle_Type',
                         title='Relación entre PIB y ventas durante recesiones')
        graph3 = dcc.Graph(figure=fig3)
        
        return [
            title,
            html.Div([graph1], style={'marginBottom': '30px'}),
            html.Div([
                html.Div([graph2], style={'width': '48%', 'display': 'inline-block', 'marginRight': '2%'}),
                html.Div([graph3], style={'width': '48%', 'display': 'inline-block'})
            ])
        ]
    
    elif report_type == 'yearly' and statistics_type == 'advertising':
        # Ejemplo: Gasto en publicidad por año
        yearly_adv = filtered_df.groupby('Year')['Advertising_Expenditure'].sum().reset_index()
        fig1 = px.line(yearly_adv, x='Year', y='Advertising_Expenditure',
                      title='Gasto en publicidad a lo largo del tiempo')
        graph1 = dcc.Graph(figure=fig1)
        
        # Gráfico secundario 1: Distribución de gasto por tipo de vehículo
        vehicle_adv = filtered_df.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        fig2 = px.pie(vehicle_adv, values='Advertising_Expenditure', names='Vehicle_Type',
                     title='Distribución de gasto publicitario por tipo de vehículo')
        graph2 = dcc.Graph(figure=fig2)
        
        # Gráfico secundario 2: Correlación entre gasto en publicidad y ventas
        fig3 = px.scatter(filtered_df, x='Advertising_Expenditure', y='Automobile_Sales',
                         color='Recession', title='Correlación entre gasto en publicidad y ventas')
        graph3 = dcc.Graph(figure=fig3)
        
        return [
            title,
            html.Div([graph1], style={'marginBottom': '30px'}),
            html.Div([
                html.Div([graph2], style={'width': '48%', 'display': 'inline-block', 'marginRight': '2%'}),
                html.Div([graph3], style={'width': '48%', 'display': 'inline-block'})
            ])
        ]
    
    else:
        # Gráfico genérico para otros casos
        fig = px.line(filtered_df.groupby('Year')['Automobile_Sales'].mean().reset_index(),
                     x='Year', y='Automobile_Sales', title='Ventas de automóviles a lo largo del tiempo')
        return [
            title,
            dcc.Graph(figure=fig),
            html.P("Seleccione otras opciones para visualizar más gráficos específicos.")
        ]

# Funciones auxiliares
def report_type_to_text(report_type):
    mapping = {
        'recession': 'Recesión',
        'yearly': 'Análisis Anual',
        'vehicle': 'Tipos de Vehículos'
    }
    return mapping.get(report_type, report_type)

def statistics_type_to_text(statistics_type):
    mapping = {
        'sales_recession': 'Ventas durante Recesión',
        'sales_vehicle': 'Ventas por Tipo de Vehículo',
        'advertising': 'Gasto en Publicidad',
        'price_sales': 'Relación Precio-Ventas',
        'unemployment': 'Impacto del Desempleo'
    }
    return mapping.get(statistics_type, statistics_type)

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(debug=True)