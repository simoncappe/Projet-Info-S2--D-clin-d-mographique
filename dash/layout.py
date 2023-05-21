import dash
from dash import dcc, html
import pandas as pd
from dash.dependencies import Input, Output, State
import geopandas
from shapely.geometry import Point, LineString, Polygon
import plotly.express as px
import numpy as np









# Initialisation de l'app
app = dash.Dash(__name__)
app.title = 'Evolution démographique de la France'
server = app.server


DEP = '93'
# Importation des shapefile 
gdp = geopandas.read_file('data\/france\/france.shp')[  #your path
    ['INSEE_COM', 'INSEE_DEP', 'geometry']]
gdp = gdp.rename(columns={'INSEE_COM':'CODGEO'})
gdp = gdp[gdp.INSEE_DEP == DEP]


geojson_dict = gdp[['CODGEO', 'geometry']].__geo_interface__#données format GEOJson

#importation des données
data = pd.read_pickle('data\demographic.pkl')[['CODGEO', 'REG', 'DEP', 'LIBGEO',
       'POPINC', 'NETMOB', 'NETNAT', 'NETMIG', 'TIME']]#your path
data = data[data.DEP == DEP]


#fonction qui sera utile dans la suite
def prepare_datamap(i,f):
    '''fonction qui prépare la dataframe à ploter
        i : année initiale
        f : année finale'''
        
    if i<=f:
        
        L = []
        for p in range(i, f+1):
            L.append(data[data.TIME == p])

        final = L[0][['CODGEO', 'REG', 'DEP','LIBGEO']]



        final['POPINC'] = L[0]['POPINC']
        final['NETNAT'] = L[0]['NETNAT']
        final['NETMOB'] = L[0]['NETMOB']    
        final['NETMIG'] = L[0]['NETMIG']
        final = final.reset_index()
        for p in range(1, len(L)):
            data_frame = L[p].reset_index()
            final['POPINC'] = final['POPINC'] + data_frame['POPINC']
            final['NETNAT'] = final['NETNAT'] +data_frame['NETNAT']
            final['NETMOB'] = final['NETMOB'] + data_frame['NETMOB']
            final['NETMIG'] = final['NETMIG'] + data_frame['NETMIG']

        final = final.reset_index()

        
        final['CAUSE'] = np.abs(final[['NETNAT', 'NETMOB', 'NETMIG']]).idxmax(
        axis=1)  # maximum des valeurs absolues des composantes
        def signe(x): return (x > 0) + (x < 0)*(-1)# Si la population a augmenté ou baissé
        final['SGN'] = signe(final['POPINC'])
        final['C'] = np.arange(len(final))
        for index in range(len(final)):
            if final['SGN'][index] == -1:
                if final['CAUSE'][index] == 'NETMOB':
                    final['C'][index] = 'NETMOB -'
                elif final['CAUSE'][index] == 'NETNAT':
                    final['C'][index] = 'NETNAT -'
                else:
                    final['C'][index] = 'NETMIG -'
            else:
                if final['CAUSE'][index] == 'NETMOB':
                    final['C'][index] = 'NETMOB +'
                elif final['CAUSE'][index] == 'NETNAT':
                    final['C'][index] = 'NETNAT +'
                else:
                    final['C'][index] = 'NETMIG +'

        
        return final










years = [2014, 2015, 2016, 2017, 2018, 2019]
token = 'pk.eyJ1Ijoic2ltb25jYXBwZSIsImEiOiJjbGh1cDdhZXMwMjB1M2ptdzR3MnNoaDZwIn0.JMQT7xIPxnssJWXmANc2oA'
mapbox_style = "mapbox://styles/theonoble/clh28k2te00mq01pg15ngcvbf"


app.layout = html.Div(
    id="root",
    children=[
        html.Div(
            id="header",
            children=[
                html.A(
                    html.Img(id="logo", src=dash.get_asset_url(
                        "logo_ocde.png")),
                    href="https://www.oecd.org/fr/",
                ),
                html.H4(children="Evolution Démographique de la France"),
                html.P(
                    id="description",
                    children="Description des variables:",
                ),
            ],
        ),
        html.Div(
            id="body",
            children=[
                html.Div(
                    id="left-column",
                    children=[
                        html.Div(
                            id="slider-container",
                            children=[
                                html.P(
                                    id="slider-text",
                                    children="Faire coulisser le curseur pour changer l'année :",
                                ),
                                dcc.Slider(
                                    id="year",
                                    min=2013,  # à remplacer par min(years)
                                    max=2019,  # à remplacer par max(years)
                                    value=2019,
                                    step = 1,
                                    marks={i:str(i) for i in range(2014,2020)}
                                ),
                            ],
                        ),
                        html.P(id="chart_selector",
                               children="Sélectionner un graphe :"),
                        dcc.Dropdown(
                            id="comp",
                            options=[
                                {'label': "Migration internationale",
                                    'value': 'NETMIG'},
                                {'label': 'Migration nationale', 'value': 'NETMOB'},
                                {'label': "Natalité et décès", 'value': 'NETNAT'},
                                {'label': "Incrément de population",
                                    'value': 'POPINC'},
                                {'label': "cause du changement de population",
                                    'value': 'C'},  # l'utilisateur voit les labels et les values corresondent à ce que'on appelle dans les callbacks.
                            ],
                            value='NETNAT',
                        ),

                        html.Div(
                            id="map-container",
                            children=[
                                dcc.Graph(
                                    id="choropleth",
                                    
                                ),
                            ]
                        )
                    ],
                ),
                html.Div(
                    id='right-column',
                    children=[
                        html.P(id='code-selector',
                               children='Sélectionner une ville'),
                        dcc.Dropdown(id='code',
                                     options=data['CODGEO'].unique(), value=data['CODGEO'].unique()[0]
                                     ),
                        dcc.Graph(
                            id="selected-data",
                            figure=dict(
                                data=[dict(x=0, y=0)],
                                layout=dict(
                                    autofill=True,
                                    margin=dict(t=75, r=50, b=100, l=50),
                                ),
                            ),
                        ),

                    ]
                )
            ],
        ),
    ],
)

@app.callback(
    Output('choropleth', 'figure'),


    Input('year', 'value'),
    Input('comp', 'value')
)
def display_choropleth(year,comp):
    carte = geopandas.GeoDataFrame(prepare_datamap(2014,year).merge(gdp,left_on = 'CODGEO',right_on = 'CODGEO',how = 'right'),geometry = 'geometry')
    u = carte['geometry'].iloc[0].centroid
    fig = px.choropleth_mapbox(
        carte,
        geojson=geojson_dict,
        locations='CODGEO',
        color=comp,
        featureidkey="properties.CODGEO",
        color_continuous_scale="Viridis",
        opacity=0.5,
        labels={comp: comp},
        center={"lon": u.x, "lat": u.y},
        zoom=7
    )

    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        mapbox=dict(accesstoken=token)
    )

    return fig


@app.callback(
    Output('selected-data', 'figure'),
    Input('choropleth', 'clickData')
)
def display_hist(clickData):
    if clickData is not None:
        code = clickData['points'][0]['location']
        #code = gdp['CODGEO'][selected_data]
        dataframe_hist = data[data.CODGEO == code]
        df = pd.DataFrame(np.arange(len(dataframe_hist)*3))
        TIME = []
        IND = []
        VALUE = []
        for i in range(2014,2020):
            TIME+=[i,i,i]
            IND+=['NETMOB','NETNAT','NETMIG']
            VALUE+=[dataframe_hist[dataframe_hist.TIME == i]['NETMOB'].iloc[0],dataframe_hist[dataframe_hist.TIME == i]['NETNAT'].iloc[0],dataframe_hist[dataframe_hist.TIME == i]['NETMIG'].iloc[0]]
        df['Année'] = TIME
        df['Indicateur'] = IND
        df['Valeur'] = VALUE
        fig = px.histogram(df,
                       x="Année",
                       y="Valeur",
                       color='Indicateur',
                       barmode="stack", nbins=23)
        fig.update_layout(
            barmode="overlay",
            bargap=0.1)

        return fig
    return {}


if __name__ == "__main__":
    app.run_server(debug=True)
