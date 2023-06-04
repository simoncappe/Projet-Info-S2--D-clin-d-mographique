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

# shapefile des communes
shp = geopandas.read_file('data\/france\/france.shp')[  # your path
    ['INSEE_COM', 'INSEE_DEP', 'geometry']]
shp['INSEE_DEP'][29275:29295] = '75'
shp = shp.rename(columns={'INSEE_COM': 'CODGEO'})
gdp = shp[shp.INSEE_DEP == '01']

# shapefile des départements
dep = geopandas.read_file('data\geometry\Tl3_fr.json')  # your path
dep = geopandas.GeoDataFrame(dep.rename(
    columns={'code': 'DEP'}), geometry='geometry')
p = dep['geometry'].iloc[0].centroid


# importation des données
dataframe = pd.read_pickle('data/demo.pkl')  # your path
dataframe = dataframe[['CODGEO', 'REG', 'DEP', 'LIBGEO',
                       'POPINC', 'NETMOB', 'NETNAT', 'NETMIG', 'POP', 'TIME']]
data = dataframe[dataframe.DEP == '01']


# fonction qui sera utile dans la suite
def prepare_datamap(i, f, data):
    '''fonction qui prépare la dataframe à ploter, 
    prend en entrée une dataframe organisée comme CODGEO DEP POP  POPINC NETNAT ... NETMOB TIME (*)
                                                  01001  01  452  12      -3    ... 0      2014
                                                  ...    ... ...          ...   ... ...    ...
                                                  ...    ... ...          ...   ... ...    ...
                                                  95026  95  3025  85     0     ... 254    2014
                                                  01001  01  458   6      7     ... -3     2015
                                                  ...    ... ...  ...    ...    ... ...    ...
                                                  ...    ... ...  ...    ...    ... ...    ...
                                                  ...    ... ...          ...   ... ...    ...
                                                  ...    ... ...          ...   ... ...    ...
                                                  95026  95   5420 7    -2      ... 2      2019
        où les variables POPINC, NETNAT, etc décrivent le changement sur l'année précédent 'TIME'                                
        et la transforme en une dataframe organisée comme  

                                                  CODGEO DEP POPI POPINC_RATE NETNAT_RATE ... NETMOB_RATE
                                                  01001  01  754  0.02        -0.015          0.01
                                                  ...    ... ...  ...         ...         ... ...
                                                  ...    ... ...  ...         ...         ... ...   
                                                  95026  95  8524 0.15        0.7         ... 0.6
        où les variables POPINC_RATE, NETNAT_RATE, etc décrivent le changement entre l'année i et f incluse.
        POPI désigne la population à l'année i  
        
        Input:  
            i : année initiale, int
            f : année finale, int
            data : donnée de la forme (*), pandas DataFrame
        Output:
            final : DataFrame préparée, pandas DataFrame
        '''

    if i <= f:
        L = []
        for p in range(i, f+1):
            # On sépare la dataframe en appliquant un masque selon l'année
            L.append(dataframe[dataframe.TIME == p])

        # dataframe finale sur laquelle on va travailler
        final = L[0][['CODGEO', 'REG', 'DEP', 'LIBGEO']]

        final['POPINC'] = L[0]['POPINC']
        final['NETNAT'] = L[0]['NETNAT']
        final['NETMOB'] = L[0]['NETMOB']
        final['NETMIG'] = L[0]['NETMIG']
        final = final.reset_index()
        for p in range(1, len(L)):
            data_frame = L[p].reset_index()
            # Somme des incrément de population pour avoir l'incrément total de i jusqu'à f
            final['POPINC'] = final['POPINC'] + data_frame['POPINC']
            # Somme des incrément naturels pour avoir le total sur i jusqu'à f
            final['NETNAT'] = final['NETNAT'] + data_frame['NETNAT']
            # Somme des mobilité nette pour avoir le total sur i jusqu'à f
            final['NETMOB'] = final['NETMOB'] + data_frame['NETMOB']
            # Somme des migartions nette pour avoir le total sur i jusqu'à f
            final['NETMIG'] = final['NETMIG'] + data_frame['NETMIG']

        final['POPI'] = dataframe[dataframe.TIME ==
                                  i].reset_index()['POP']  # Population initiale
        final = final.reset_index()
        final = final[final.columns[2:]]  # clean

        # Calcul des incréments en pourcentages
        final['POPINC_RATE'] = final['POPINC'] / \
            final['POPI']  # POPINC_RATE = (POPF-POPI)/POPI
        final['NETNAT_RATE'] = final['NETNAT'] / \
            final['POPI']  # NETNAT_RATE = NETNAT/POPI
        final['NETMIG_RATE'] = final['NETMIG'] / \
            final['POPI']  # NETMIG_RATE = NETMIG/POPI
        final['NETMOB_RATE'] = final['NETMOB'] / \
            final['POPI']  # NETMOB_RATE = NETMOB/POPI

        # crétaion de la colonne reflétant la cause principale du changement démographique sur l'année
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

        final = final[['CODGEO', 'REG', 'DEP', 'LIBGEO', 'POPINC_RATE',
                       'NETNAT_RATE', 'NETMIG_RATE', 'NETMOB_RATE', 'C']]

        return final


years = [2014, 2015, 2016, 2017, 2018, 2019]
token = 'pk.eyJ1Ijoic2ltb25jYXBwZSIsImEiOiJjbGh1cDdhZXMwMjB1M2ptdzR3MnNoaDZwIn0.JMQT7xIPxnssJWXmANc2oA'
mapbox_style = "mapbox://styles/theonoble/clh28k2te00mq01pg15ngcvbf"


# Layout
app.layout = html.Div(
    id="root",
    children=[
        html.Div(
            id="header",#header avec titre
            children=[
                html.A(
                    html.Img(id="logo", src=dash.get_asset_url(
                        "logo_ocde.png")),
                    href="https://www.oecd.org/fr/",
                ),
                html.H4(children="Evolution Démographique de la France"),
            ],
        ),
        html.Div(
            id="body",
            children=[
                html.Div(
                    id="description",
                    children=[
                        html.P(
                            id = "title",
                            children = "Description des variables"
                        ),
                        html.Ul(id = 'list',
                                children = [
                                    html.Li(id = 'POPINC',
                                            children = "Variation de la Population : Incrément de populationau sein de la commune entre le premier Janvier de l\'année initiale et le premier Janvier de l\'année finale"
                                            ),
                                    html.Li(id = "NETNAT",
                                            children = "Taux de solde naturel : Différence entre le nombre de naissances et le nombre de décès enregistrés au sein de la commune entre le premier Janvier de l\'année initiale et le premier Janvier de l\'année finale "
                                            ),
                                    html.Li(id = "NETMOB",
                                            children = "Taux de mobilité : Différence entre le nombre de personnes ayant déménagé dans la commune qui vivaient déjà en France et le nombre de personne vivant dans la commune et qui ont déménagé autre part en France entre le premier Janvier de l\'année initiale et le premier Janvier de l\'année finale"
                                            ),
                                    html.Li(id = "NETMIG",
                                            children = "Taux de migration : Différence entre le nombre de personnes ayant déménagé dans la commune qui vivaient à l'étranger et le nombre de personnes vivant dans la commune et qui ont déménagé à l'étranger"
                                            ),
                                    html.Li(id = "C",
                                            children = "Cause du changement de population : Maximum en valeur absolue des trois composantes présentées ci dessus, accompagnée d'un indicateur de si la population a augmenté ou diminuée"
                                            )
                                ]
                        )
                    ]
                ),
                html.Div(
                    id="slider-container",
                    children=[
                        html.P(
                            id="slider-text",
                            children="Faire coulisser le curseur pour changer l'année :",
                        ),
                        dcc.RangeSlider(#slider pour changer l'année de départ et d'arrivée
                            id="years",
                            min=2014,
                            max=2019,
                            value=[2014, 2019],
                            step=1,
                            marks={i: {'label': str(i), 'style': {
                                'color': 'white'}} for i in range(2014, 2020)},
                        ),
                    ],
                ),
                html.Div(
                    id="selection_graphe",#séléction du graphe: POPINC, cause, etc...
                    children=[
                        html.P(id="chart_selector",
                               children="Sélectionner un graphe :"),
                        dcc.Dropdown(
                            id="comp",
                            options=[
                                {'label': "Taux de migration internationale",
                                    'value': 'NETMIG_RATE'},
                                {'label': 'Taux de migration nationale',
                                    'value': 'NETMOB_RATE'},
                                {'label': "Taux de solde naturel",
                                    'value': 'NETNAT_RATE'},
                                {'label': "Variation de la population",
                                    'value': 'POPINC_RATE'},
                                {'label': "cause du changement de population",
                                    'value': 'C'},  # l'utilisateur voit les labels et les values corresondent à ce que'on appelle dans les callbacks.
                            ],
                            value='POPINC_RATE',
                        ),
                    ]
                ),
                html.Div(
                    id="carte",
                    children=[
                        html.Button('Revenir à la carte dep',
                                    id='reset-button', n_clicks=0),#Boutton pour revenir à la carte des département 
                                                                   #une fois qu'on est passé à la carte des communes
                        html.Div(
                            id="map-container",#contient la carte
                            children=[
                                dcc.Graph(
                                    id="choropleth",
                                ),
                            ]
                        ),
                    ],
                ),
                html.Div(
                    id="graphe",
                    children=[
                        html.P(id='code-selector',
                               children='Cliquez sur une ville sur la carte'),

                        dcc.Graph(
                            id="selected-data",#contient l'histogramme qui apparaît une fois qu'on a cliqué sur une ville sur la carte
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
#fin du layout

#callback sur la carte choropleth
@app.callback(
    Output('choropleth', 'figure'),
    Output('reset-button', 'n_clicks'),
    Input('choropleth', 'clickData'),#cliquer sur un département le fait apparaitre au niveau communal
    Input('reset-button', 'n_clicks'),#cliquer sur le boutton fait réapparaître la carte des départements
    Input('comp', 'value'),#donnée du type de graphe qu'on souhaite
    Input('years', 'value')#donnée du slider avec l'année
)
def update_map(clickData, n_clicks, comp, years):
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if (trigger_id == 'choropleth') and (clickData is not None):#si on a cliqué sur la carte des départements
        DEP = clickData['points'][0]['location']
        fig = generate_com_map(years, comp, DEP)
        return fig, 0
    else:
        return generate_dep_map(years, comp), 0 #sinon

#callback sur l'histogramme
@app.callback(
    Output('selected-data', 'figure'),
    Input('choropleth', 'clickData')#cliquer sur une commune fait apparaître son graphe
)
def display_hist(clickData):

    if clickData is not None:
        code = clickData['points'][0]['location'] #l'index de la commune choisie = CODGEO
        dataframe_hist = dataframe[dataframe.CODGEO == code]
        if dataframe_hist.empty: #vérifie si la dataframe n'est pas vide
            return {}
        else:
            #travail sur la dataframe pour la formater aux exigences de la fonction px.histogram qui n'accepte que la forme:
            #               TIME INDICATEUR VALUE 
            #               2014 NETNAT     3
            #               2014 NETMOB     7
            #               ...  ...        ...
            #               ...  ...        ...
            #               2019 NETMIG     3
            df = pd.DataFrame(np.arange(len(dataframe_hist)*3))#dataframe qui ira dans px.historam
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
            #fin du formatage
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


def generate_com_map(years, comp, DEP):
    '''Fonction qui prépare les données pour afficher la carte des communes
    Input : 
        years : liste de deux éléments [année initiale,année finale], array-like ou liste à deux éléments au moins
        comp  : souhait de la carte à afficher entre 'POPINC_RATE','NETNAT_RATE','NETMOB_RATE','NETMIG_RATE' et 'C', str
        DEP   : département à afficher, str
    Output:
        fig   : plotly.express figure 
    '''
    gdp = shp[shp.INSEE_DEP == DEP]
    data = dataframe[dataframe.DEP == DEP]
    geojson_dict = gdp[['CODGEO', 'geometry']].__geo_interface__
    carte = geopandas.GeoDataFrame(prepare_datamap(years[0], years[1], data).merge(#utilisation de la fonction prepare_datamap définie au début
        gdp, left_on='CODGEO', right_on='CODGEO', how='right'), geometry='geometry')

    if not (carte.empty):
        u = carte['geometry'].iloc[0].centroid #accès au centroid d'un des Polygons pour savoir où zoomer
        fig = px.choropleth_mapbox(
            carte,
            geojson=geojson_dict,
            locations='CODGEO',
            color=comp,
            featureidkey="properties.CODGEO",
            color_continuous_scale="Viridis",
            opacity=0.5,
            labels={'NETNAT_RATE': 'Taux de changement naturel (net)', 'NETMIG_RATE': 'Taux de migration (net)',
                    'NETMOB_RATE': 'Taux de mobilité (net)', 'POPINC_RATE': 'Variation de population',
                    'C': 'Cause du changement démographique', 'NETNAT +': 'changement naturel fait augmenter', 'NETNAT -': 'changement naturel fait diminuer',
                    'NETMIG +': 'Migration fait augmenter', 'NETMIG -': 'Migration fait baisser',
                    'NETMOB +': 'Mobilité fait augmenter', 'NETMOB -': 'Mobilité fait baisser'},
            center={"lon": u.x, "lat": u.y},
            zoom=7, title='Démographie dans le'+DEP, hover_name='LIBGEO'
        )
        fig.update_layout(
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            mapbox=dict(accesstoken=token)
        )

        return fig


def generate_dep_map(years, comp):
    '''Fonction qui prépare les données pour afficher la carte des départements
    Input: 
        years : liste de deux éléments [année initiale,année finale], array-like ou liste à deux éléments au moins
        comp  : souhait de la carte à afficher entre 'POPINC_RATE','NETNAT_RATE','NETMOB_RATE','NETMIG_RATE' et 'C', str
    Output:
        fig   : plotly.express figure 
    '''
    i = years[0]
    f = years[1]
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

    data_dep['POPI'] = dataframe[dataframe.TIME == i].reset_index()['POP']
    data_dep = data_dep.reset_index()
    data_dep = data_dep[data_dep.columns[2:]]

    data_dep = data_dep[['DEP', 'POPINC', 'NETMOB',
                         'NETNAT', 'NETMIG', 'POPI']].groupby('DEP').sum()

    data_dep['POPINC_RATE'] = data_dep['POPINC']/data_dep['POPI']
    data_dep['NETNAT_RATE'] = data_dep['NETNAT']/data_dep['POPI']
    data_dep['NETMIG_RATE'] = data_dep['NETMIG']/data_dep['POPI']
    data_dep['NETMOB_RATE'] = data_dep['NETMOB']/data_dep['POPI']

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
                               labels={'NETNAT_RATE': 'Taux de changement naturel (net)', 'NETMIG_RATE': 'Taux de migration (net)', 'NETMOB_RATE': 'Taux de mobilité (net)', 'POPINC_RATE': 'Variation de population',
                                       'C': 'Cause du changement démographique', 'NETNAT+': 'changement naturel fait augmenter', 'NETNAT -': 'changement naturel fait diminuer', 'NETMIG +': 'Migration fait augmenter', 'NETMIG -': 'Migration fait baisser', 'NETMOB +': 'Mobilité fait augmenter', 'NETMOB -': 'Mobilité fait baisser'},
                               hover_name='nom',
                               center={"lon": p.x, "lat": p.y},
                               zoom=4,
                               
                               )
    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        mapbox=dict(accesstoken=token)
    )
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
