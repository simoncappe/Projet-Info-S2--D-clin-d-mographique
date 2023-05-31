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


# Importation des shapefile
shp = geopandas.read_file('data\/france\/france.shp')[  # your path
    ['INSEE_COM', 'INSEE_DEP', 'geometry']]
shp['INSEE_DEP'][29275:29295] = '75'

shp = shp.rename(columns={'INSEE_COM': 'CODGEO'})
gdp = shp[shp.INSEE_DEP == '01']

dep = geopandas.read_file('data\geometry\Tl3_fr.json')  # your path
dep = geopandas.GeoDataFrame(dep.rename(
    columns={'code': 'DEP'}), geometry='geometry')
p = dep['geometry'].iloc[0].centroid


# importation des données
dataframe = pd.read_pickle('data\demographic.pkl')  # your path
dataframe = dataframe[['CODGEO', 'REG', 'DEP', 'LIBGEO',
                       'POPINC', 'NETMOB', 'NETNAT', 'NETMIG', 'TIME']]
data = dataframe[dataframe.DEP == '01']

# fonction qui sera utile dans la suite


def prepare_datamap(i, f, data):
    '''fonction qui prépare la dataframe à ploter
        i : année initiale
        f : année finale'''

    if i <= f:
        L = []
        for p in range(i, f+1):
            L.append(dataframe[dataframe.TIME == p])

        final = L[0][['CODGEO', 'REG', 'DEP', 'LIBGEO']]

        final['POPINC'] = L[0]['POPINC']
        final['NETNAT'] = L[0]['NETNAT']
        final['NETMOB'] = L[0]['NETMOB']
        final['NETMIG'] = L[0]['NETMIG']
        final = final.reset_index()
        for p in range(1, len(L)):
            data_frame = L[p].reset_index()
            final['POPINC'] = final['POPINC'] + data_frame['POPINC']
            final['NETNAT'] = final['NETNAT'] + data_frame['NETNAT']
            final['NETMOB'] = final['NETMOB'] + data_frame['NETMOB']
            final['NETMIG'] = final['NETMIG'] + data_frame['NETMIG']

        final = final.reset_index()

        final['CAUSE'] = np.abs(final[['NETNAT', 'NETMOB', 'NETMIG']]).idxmax(
            axis=1)  # maximum des valeurs absolues des composantes

        # Si la population a augmenté ou baissé
        def signe(x): return (x > 0) + (x < 0)*(-1)
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

figdep = px.choropleth_mapbox(
    dep,
    geojson=dep.__geo_interface__,
    locations='DEP',
    hover_name='nom',
    featureidkey="properties.DEP",
    color_continuous_scale="Viridis",
    opacity=0.5,
    center={"lon": p.x, "lat": p.y},
    zoom=4
)
figdep.update_layout(
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    mapbox=dict(accesstoken=token)
)


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
                    children="Description des variabes:",
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
                                    min=2013,
                                    max=2019,
                                    value=2019,
                                    step=1,
                                    marks={i: str(i)
                                           for i in range(2014, 2020)}
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
                            value='POPINC',
                        ),
                        html.Button('Revenir à la carte dep',
                                    id='reset-button', n_clicks=0),
                        html.Div(

                            id="map-container",
                            children=[

                                dcc.Graph(
                                    id="choropleth",
                                ),
                                # dcc.Graph(
                                #    id="dep",
                                #    figure=figdep
                                # )
                            ]
                        )
                    ],
                ),
                html.Div(
                    id='right-column',
                    children=[
                        html.P(id='code-selector',
                               children='Cliquez sur une ville sur la carte'),

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
    Input('choropleth', 'clickData'),
    Input('reset-button', 'n_clicks'),
    Input('comp', 'value'),
    Input('year', 'value')
)
def update_map(clickData, n_clicks, comp, year):
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if (trigger_id == 'reset-button'):
        return generate_dep_map(year, comp)
    if (trigger_id == 'choropleth') and (clickData is not None):
        DEP = clickData['points'][0]['location']
        fig = generate_com_map(year, comp, DEP)
        return fig
    else:
        return generate_dep_map(year, comp)


@app.callback(
    Output('selected-data', 'figure'),
    Input('choropleth', 'clickData')
)
def display_hist(clickData):

    if clickData is not None:
        code = clickData['points'][0]['location']
        dataframe_hist = dataframe[dataframe.CODGEO == code]
        if dataframe_hist.empty:
            return {}
        else:

            df = pd.DataFrame(np.arange(len(dataframe_hist)*3))
            TIME = []
            IND = []
            VALUE = []
            for i in range(2014, 2020):
                TIME += [i, i, i]
                IND += ['NETMOB', 'NETNAT', 'NETMIG']
                VALUE += [dataframe_hist[dataframe_hist.TIME == i]['NETMOB'].iloc[0], dataframe_hist[dataframe_hist.TIME == i]
                          ['NETNAT'].iloc[0], dataframe_hist[dataframe_hist.TIME == i]['NETMIG'].iloc[0]]
            df['Année'] = TIME
            df['Indicateur'] = IND
            df['Valeur'] = VALUE
            fig = px.histogram(df,
                               x="Année",
                               y="Valeur",
                               color='Indicateur',
                               barmode="stack", nbins=23, title='Démographie à ' + dataframe[dataframe.CODGEO == code]['LIBGEO'].iloc[0])
            fig.update_layout(
                barmode="overlay",
                bargap=0.1)

            return fig
    return {}


def generate_com_map(year, comp, DEP):
    gdp = shp[shp.INSEE_DEP == DEP]
    data = dataframe[dataframe.DEP == DEP]
    geojson_dict = gdp[['CODGEO', 'geometry']].__geo_interface__
    carte = geopandas.GeoDataFrame(prepare_datamap(2014, year, data).merge(
        gdp, left_on='CODGEO', right_on='CODGEO', how='right'), geometry='geometry')
    if carte.empty:
        x = 3
    else:
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
            zoom=7, title='Démographie dans le'+DEP, hover_name='LIBGEO'
        )
        fig.update_layout(
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            mapbox=dict(accesstoken=token)
        )

        return fig


def generate_dep_map(year, comp):
    i = 2014
    f = year
    L = []
    for p in range(i, f+1):
        L.append(dataframe[dataframe.TIME == p])

    data_dep = L[0][['CODGEO', 'REG', 'DEP', 'LIBGEO']]

    data_dep['POPINC'] = L[0]['POPINC']
    data_dep['NETNAT'] = L[0]['NETNAT']
    data_dep['NETMOB'] = L[0]['NETMOB']
    data_dep['NETMIG'] = L[0]['NETMIG']
    data_dep = data_dep.reset_index()
    for p in range(1, len(L)):
        data_frame = L[p].reset_index()
        data_dep['POPINC'] = data_dep['POPINC'] + data_frame['POPINC']
        data_dep['NETNAT'] = data_dep['NETNAT'] + data_frame['NETNAT']
        data_dep['NETMOB'] = data_dep['NETMOB'] + data_frame['NETMOB']
        data_dep['NETMIG'] = data_dep['NETMIG'] + data_frame['NETMIG']

    data_dep = data_dep[['DEP', 'POPINC', 'NETMOB',
                         'NETNAT', 'NETMIG']].groupby('DEP').sum()
    p = dep['geometry'].iloc[0].centroid
    data_dep['CAUSE'] = np.abs(data_dep[['NETNAT', 'NETMOB', 'NETMIG']]).idxmax(
        axis=1)  # maximum des valeurs absolues des composantes

    # Si la population a augmenté ou baissé
    def signe(x): return (x > 0) + (x < 0)*(-1)
    data_dep['SGN'] = signe(data_dep['POPINC'])
    data_dep['C'] = np.arange(len(data_dep))
    for index in range(len(data_dep)):
        if data_dep['SGN'][index] == -1:
            if data_dep['CAUSE'][index] == 'NETMOB':
                data_dep['C'][index] = 'NETMOB -'
            elif data_dep['CAUSE'][index] == 'NETNAT':
                data_dep['C'][index] = 'NETNAT -'
            else:
                data_dep['C'][index] = 'NETMIG -'
        else:
            if data_dep['CAUSE'][index] == 'NETMOB':
                data_dep['C'][index] = 'NETMOB +'
            elif data_dep['CAUSE'][index] == 'NETNAT':
                data_dep['C'][index] = 'NETNAT +'
            else:
                data_dep['C'][index] = 'NETMIG +'

    data_dep = geopandas.GeoDataFrame(data_dep.merge(
        dep, left_on='DEP', right_on='DEP', how='right'), geometry='geometry')
    fig = px.choropleth_mapbox(data_dep, geojson=data_dep.__geo_interface__, locations='DEP', color=comp, featureidkey="properties.DEP",
                               color_continuous_scale="Viridis",
                               opacity=0.5,
                               labels={comp: comp},
                               hover_name='nom',
                               center={"lon": p.x, "lat": p.y},
                               zoom=4
                               )
    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        mapbox=dict(accesstoken=token)
    )

    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
