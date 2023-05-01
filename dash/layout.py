import dash
from dash import dcc, html
import pandas as pd
from dash.dependencies import Input, Output, State
import geopandas
from shapely.geometry import Point, LineString, Polygon
import plotly.express as px

# Initialisation de l'app
app = dash.Dash(__name__)
app.title = 'Evolution démographique de la France'
server = app.server


#Importation des données (uniquement de l'immigration)
data_arr_mun = geopandas.read_file('../data_geom/arrond_mun/ARRONDISSEMENT_MUNICIPAL.shp')
data_arr_mun = data_arr_mun[['ID', 'NOM', 'NOM_M', 'INSEE_COM', 'POPULATION', 'geometry']]
data_commune = geopandas.read_file('../data_geom/commune/COMMUNE.shp')
data_commune = data_commune[['ID', 'NOM', 'NOM_M', 'INSEE_COM', 'geometry']]

data_complete = data_commune.append(data_arr_mun)

data_migration2019 = pd.read_csv('../data_migration/base-flux-mobilite-residentielle-2019.csv', sep=';').astype('str')
data_migration2019 = data_migration2019[data_migration2019['DCRAN']=='99999']
carte = geopandas.GeoDataFrame(data_migration2019.merge(data_complete, left_on='LIBGEO', right_on='NOM', how='outer'), geometry='geometry')
carte = carte[['CODGEO', 'NBFLUX_C19_POP01P', 'NOM', 'ID', 'INSEE_COM', 'geometry']]
carte['NBFLUX_C19_POP01P'] = carte['NBFLUX_C19_POP01P'].astype(float)
carte['NBFLUX_C19_POP01P'] = carte['NBFLUX_C19_POP01P'].fillna(0.)
carte['Année']=2019

geojson_dict = data_complete['geometry'].__geo_interface__


years = [2000, 2019, 2023]
mapbox_access_token = "pk.eyJ1IjoidGhlb25vYmxlIiwiYSI6ImNsaDI0dDEwZjFhOGIzZGp1ZzRwMHg4NWsifQ.hKTjHzcgmTxPZ9NMzFBTQg"
mapbox_style = "mapbox://styles/theonoble/clh28k2te00mq01pg15ngcvbf"


app.layout = html.Div(
    id = "root",
    children = [
        html.Div(
            id = "header",
            children = [
                html.A(
                    html.Img(id="logo", src = dash.get_asset_url("logo_ocde.png")),
                    href = "https://www.oecd.org/fr/",
                ),
                html.H4(children = "Evolution Démographique de la France"),
                html.P(
                    id = "description",
                    children = "Voilà comment on obtient les données",
                ),
            ],
        ),
        html.Div(
            id = "body",
            children = [
                html.Div(
                    id = "left-column",
                    children = [
                        html.Div(
                            id = "slider-container",
                            children = [
                                html.P(
                                    id = "slider-text",
                                    children = "Faire coulisser le curseur pour changer l'année :",
                                ),
                                dcc.Slider(
                                    id = "choix_année",
                                    min = 2000, #à remplacer par min(years)
                                    max = 2023, #à remplacer par max(years)
                                    value = 2019,
                                    marks = {
                                        str(year): {
                                            "label": str(year),
                                        }
                                        for year in years
                                    }
                                ),
                            ],
                        ),
                        html.Div(
                            id = "map-container",
                            children = [
                                dcc.Graph(
                                    id="choropleth",
                                    figure=dict(
                                        layout=dict(
                                            mapbox=dict(
                                                layers=[],
                                                accesstoken=mapbox_access_token,
                                                style=mapbox_style,
                                                center=dict(
                                                    lat=38.72490, lon=-95.61446
                                                ),
                                                pitch=0,
                                                zoom=3.5,
                                            ),
                                            autosize=True,
                                        ),
                                    ),
                                ),
                            ]
                        )
                    ],
                ),
                html.Div(
                    id = "right-column",
                    children = [
                        html.P(id = "chart_selector", children = "Sélectionner un graphe :"),
                        dcc.Dropdown(
                            id = "graph_dropdown",
                            options = [
                                {'label': "Migration internationale", 'value': 'NETMIG'},
                                {'label': 'Migration nationale', 'value': 'NETMOB'},
                                {'label': "Natalité et décès", 'value':'NETNAT'}  #l'utilisateur voit les labels et les values corresondent à ce que'on appelle dans les callbacks.
                            ],
                            value = 'NETNAT',
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
    Output("choropleth", "figure"),
    Input("choix_année", "value"),
)
def display_choropleth(choix_année):
    fig = px.choropleth(
        carte[carte['Année']==f'choix_année'],
        geojson=geojson_dict,
        color=carte[carte['Année']==f'choix_année']['NBFLUX_C19_POP01P'],
        locations="CODGEO",
        featureidkey="properties.CODGEO",
        projection="mercator",
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
