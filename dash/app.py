from dash import Dash, dcc, html, Input, Output
import dash
from dash import dcc
from dash import html
import geopandas as gpd
import plotly.express as px

import pandas as pd

import matplotlib.pyplot as plt


# data
VARPOP = pd.read_csv('data\VARPOP.csv')
# extraction des shapefiles
shp_arr = gpd.read_file(
    'data\Arrondissements municipal/ARRONDISSEMENT_MUNICIPAL.shp')  # arrondissements de Paris,Lyon et Marseille
shp_arr['INSEE_COM'] = shp_arr['INSEE_ARM']
shp_arr = shp_arr[['ID', 'NOM', 'NOM_M',
                   'INSEE_COM', 'geometry']]
shp_commune = gpd.read_file(
    'data\COMMUNE\COMMUNE.shp')  # Communes de France
shp_commune = shp_commune[['ID', 'NOM',
                           'INSEE_DEP', 'NOM_M', 'INSEE_COM', 'geometry']]
gdp = shp_commune.append(shp_arr)
gdp = gdp[(gdp.INSEE_COM != '75056') & (
    gdp.INSEE_COM != '69123') & (gdp.INSEE_COM != '13055')]
index = list(gdp['INSEE_COM'])
gdp = gpd.GeoDataFrame(gdp).set_index('INSEE_COM').sort_index(
).reset_index()[['INSEE_COM', 'INSEE_DEP', 'NOM', 'NOM_M', 'geometry']]

data = gpd.GeoDataFrame(VARPOP.merge(
    gdp, how='right', left_on='CODGEO', right_on='INSEE_COM'), geometry='geometry')

# data VARPOP + geometry
data = data[['CODGEO', 'NETNAT', 'NETMIG', 'NETMOB', 'geometry']]


# conversion des géométries en format geojson
geojson_dict = data['geometry'].__geo_interface__


# Données extraites


app = Dash(__name__)

app.layout = html.Div(
    [
        html.H4("MAP"),
        html.P("Choisir composante :"),
        dcc.RadioItems(
            id="composante",
            options=["NETNAT", "NETMOB", "NETMIG"],
            value="NETNAT",
            inline=True,
        ),
        dcc.Graph(id="graph"),
    ]
)


@app.callback(
    Output("graph", "figure"),
    Input("composante", "value"),
)
def display_choropleth(composante):

    fig = px.choropleth(
        data,
        geojson=geojson_dict,
        color=composante,
        locations="CODGEO",
        featureidkey="properties.CODGEO",
        projection="mercator",
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
