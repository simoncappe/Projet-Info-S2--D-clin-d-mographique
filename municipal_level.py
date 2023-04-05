import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import geopandas
from shapely.geometry import Point, LineString, Polygon, MultiPolygon



g = ...  # dataframe qui contient les coordonnées des polygons (télécharger sur internet, site de l'INSEE par exemple)



# Là il faut en général faire quelques efforts pour sortir les polygones des dataframes trouvées sur internet:

Names = []

G = []


for i in g['features']:
    Names+=...


    if i['geometry']['type'] == 'Polygon':
        ...

    else:
        ...








df = ... # données au niveau municipal téléchargé sur le site de l'OCDE (ou par API si maitrise)
G_bis=[]#pour bien associer le bon polygone à la bonne ville, il faut en général faire une petite manip pour bien associer les deux
for i in df['Région']:
    ...
    G_bis+=...




gdp = geopandas.GeoDataFrame(df, geometry=G_bis)
gdp.plot("Value", legend=True)
plt.show()
plt.close()
