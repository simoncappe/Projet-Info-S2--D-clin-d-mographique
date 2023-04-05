import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import geopandas
from shapely.geometry import Point, LineString, Polygon, MultiPolygon

boundaries_aude=pd.read_csv('data\geometry\geometry_dep11.csv')

Names_commune = list(boundaries_aude['NOM'])
Id_commune = list(boundaries_aude['ID'])
G_commune = [boundaries_aude['geometry']] #attention, type Series


geometry_commune = pd.DataFrame(Names_commune, columns=['Commune'], index=np.arange(len(Names_commune)))
geometry_commune['Id']=Id_commune

data_france_commune = pd.read_csv('data\data_csv\pop_municipale.csv', sep=';')

'''
R=[]
for commune in data_france_commune['Libellé']:
    p=geometry_commune[geometry_commune['Commune']==commune]
    R.append(G_commune.loc(p))
gpd=geopandas.GeoDataFrame(data_france_commune, geometry=R)

plt.title('Population en 2019')
plt.legend()
plt.show()
'''
R = []
for commune in data_france_commune['Libellé']:
    pass
test=data_france_commune['Libellé'].iloc(0)
print(test)