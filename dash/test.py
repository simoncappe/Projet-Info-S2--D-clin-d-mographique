from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import geopandas as gpd
import pandas as pd
import numpy as np

geo = gpd.read_file('.\data\geometry\Tl2_fr.json')

df = pd.read_csv('.\data\data_csv\data_tl2_fr.csv', usecols=['REG_ID', 'Région',
                                                           'Indicateur', 'SEX', 'Genre', 'POS', 'Année', 'Value'])


indi = df['Indicateur'][3]
df = df[(df.Indicateur == indi) & (df.Année == 2005) & (df.SEX == 'T')]

data = df.merge(geo, left_on='Région', right_on='libgeo',
                how='right')[['libgeo', 'Value']]

data['A'] = np.random.exponential(80, 18)
data['B'] = np.random.exponential(80, 18)
data['C'] = np.random.exponential(80, 18)
geojson_dict = geo.__geo_interface__







fig = px.choropleth(
        data,
        geojson=geojson_dict,
        color='A',
        locations="libgeo",
        featureidkey="properties.libgeo",
        projection="mercator",
        range_color=[0, 200],labels = {'A':'blablablaaaaaaaaaaaaaaaaaaaaaaaa'}
    )
fig.update_geos(fitbounds="locations", visible=False)

fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0},coloraxis_colorbar_title_side="right")
    
fig.show()