import geopandas 
import numpy as np
import plotly.express 

import pandas as pd

import matplotlib.pyplot as plt

#data = geopandas.read_file('data\/test\/test.shp').iloc[:10]
#geojson_dict = data[['CODGEO','geometry']].__geo_interface__


data = geopandas.read_file('data\geometry\Tl3_fr.json')#polygones
data['A'] = np.random.exponential(80, len(data)) #création d'une colonne avec des données au hasard
geojson_dict = data[['code','geometry']].__geo_interface__#dictionnaire geojson

fig = plotly.express.choropleth(
        data,
        geojson=geojson_dict,
        color='A', #NETNAT
        locations="code",#CODGEO
        featureidkey="properties.code",#propreties.CODGEO
        projection="mercator",    
    )
fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
fig.show()



