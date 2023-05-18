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


# Importation des données (uniquement de l'immigration)
'''data_arr_mun = geopandas.read_file('data\Arrondissements municipal\ARRONDISSEMENT_MUNICIPAL.shp')
data_arr_mun = data_arr_mun[['ID', 'NOM', 'NOM_M', 'INSEE_COM', 'POPULATION', 'geometry']]
data_commune = geopandas.read_file('data\COMMUNE\COMMUNE.shp')
data_commune = data_commune[['ID', 'NOM', 'NOM_M', 'INSEE_COM', 'geometry']]

data_complete = data_commune.append(data_arr_mun)'''

gdp = geopandas.read_file('data\/france\/france.shp')[
    ['INSEE_COM', 'INSEE_DEP', 'geometry']]
data_complete = gdp

data = pd.read_csv('data\VARPOP.csv')
data['DEP'][29275:29295] = '75'


df = data.merge(data_complete, left_on='CODGEO',
                right_on='INSEE_COM', how='right')
#print(df['DEP'].unique())
df = df[(df.DEP == '38') | (df.DEP == '01')]# | (df.DEP == '69') | (df.DEP == '42') | (
    #df.DEP == '71') | (df.DEP == '03') | (df.DEP == '58') | (df.DEP == '21')]

carte = geopandas.GeoDataFrame(df, geometry='geometry')

'''
dataframe = pd.read_csv('data\/app.csv')
dataframe['CODGEO'] = dataframe['CODGEO'].astype(str)
print(dataframe['CODGEO'].unique())
'''
dataframe_hist = pd.read_csv('data\cc.csv')
dr = dataframe_hist.merge(df,left_on = 'CODGEO',right_on = 'CODGEO',how = 'right')


geojson_dict = carte[['CODGEO', 'geometry']].__geo_interface__


years = [2014, 2015, 2016, 2017, 2018, 2019]
mapbox_access_token = "pk.eyJ1IjoidGhlb25vYmxlIiwiYSI6ImNsaDI0dDEwZjFhOGIzZGp1ZzRwMHg4NWsifQ.hKTjHzcgmTxPZ9NMzFBTQg"
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
                    children="Voilà comment on obtient les données",
                ),
            ],
        ),
        html.Div(
            id="body",
            children=[
                html.Div(
                    id="left-column",
                    children=[
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
                                    'value': 'C'},# l'utilisateur voit les labels et les values corresondent à ce que'on appelle dans les callbacks.
                            ],
                            value='NETNAT',
                        ),
                        
                        html.Div(
                            id="map-container",
                            children=[
                                dcc.Graph(
                                    id="choropleth",
                                    #'''figure=dict(
                                    #    layout=dict(
                                    #        mapbox=dict(
                                    #            layers=[],
                                    #            accesstoken=mapbox_access_token,
                                    #            style=mapbox_style,
                                    #            center=dict(
                                    #                lat=38.72490, lon=-95.61446
                                    #            ),
                                    #            pitch=0,
                                    #            zoom=3.5,
                                    #        ),
                                    #        autosize=True,
                                    #    ),
                                    #),'''
                                ),
                            ]
                        )
                    ],
                ),
                html.Div(
                    id='right-column',
                    children=[
                        html.P(id = 'code-selector', children = 'Sélectionner une ville'),
                        dcc.Dropdown(id = 'code',
                                     options = dr['CODGEO'].unique(),value = dr['CODGEO'].unique()[0]
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

'''html.Div(
                            id="slider-container",
                            children=[
                                html.P(
                                    id="slider-text",
                                    children="Faire coulisser le curseur pour changer l'année :",
                                ),
                                dcc.Slider(
                                    id="choix_année",
                                    min=2000,  # à remplacer par min(years)
                                    max=2023,  # à remplacer par max(years)
                                    value=2019,
                                    marks={
                                        str(year): {
                                            "label": str(year),
                                        }
                                        for year in years
                                    }
                                ),
                            ],
                        ),'''
                        





@app.callback(
    Output('choropleth', 'figure'),
    

    # Input('year', 'value'),
    Input('comp', 'value')
)



def display_choropleth(comp):
    fig = px.choropleth(
        carte,
        geojson=geojson_dict,
        color=comp,
        locations='CODGEO',
        featureidkey='properties.CODGEO',
        projection="mercator",
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig


@app.callback(
    Output('selected-data','figure'),
       Input('code','value')
)
def display_hist(code):
    data = dataframe_hist[dataframe_hist.CODGEO == code]
    f = pd.DataFrame(np.arange(18))
    f['TIME'] = [2014,2014,2014,2015,2015,2015,2016,2016,2016,2017,2017,2017,2018,2018,2018,2019,2019,2019]
    L=[]
    for k in range(6):
        L+=['NETMIG','NETMOB','NETNAT']
    f['IND'] = L
    f['VALUE'] = list(data.iloc[0][1:19])
    fig =px.histogram(f,
                   x="TIME",
                   y="VALUE",
                   color="IND",
                   barmode="stack", nbins=23,title = 'évolution démographique dans le '+str(code))
    fig.update_layout(
    barmode="overlay",
    bargap=0.1)
    
    return fig






if __name__ == "__main__":
    app.run_server(debug=True)
