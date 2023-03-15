import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import geopandas
from shapely.geometry import Point, LineString, Polygon, MultiPolygon

dep=pd.read_json('tl3_fr.json')
Names_dep=[]
Id_dep=[]
G_dep=[]


for i in dep['features'] :
    Names_dep.append(i['properties']['nom'])
    Id_dep.append(i['properties']['code'])

    if i['geometry']['type']=='Polygon' :
        coords_dep = i['geometry']['coordinates'][0]
        G_dep.append(Polygon(coords_dep))
       

    else :
        coords_dep = [Polygon(p[0]) for p in i['geometry']['coordinates']]
        G_dep.append(MultiPolygon(coords_dep))
      

dep_pd = pd.DataFrame(Names_dep, columns=['Departements'])
dep_pd['Id_dep']=Id_dep


geo_dep = geopandas.GeoDataFrame(dep_pd, geometry=G_dep)



df_dep=pd.read_csv('data_tl3_fr.csv',usecols=['TL','REG_ID', 'Région', 
       'Indicateur', 'SEX', 'Genre', 'POS','Année','Value'])
df_dep=df_dep[(df_dep.TL==3)&(df_dep.Année==2005)]
df_dep=df_dep.reset_index(drop=True)

print(df_dep)

R=[]
for i in df_dep['Région']:
    p=dep_pd[dep_pd['Departements']==i].index.values[0]
    R.append(G_dep[p])
gpd=geopandas.GeoDataFrame(df_dep,geometry=R)
gpd.plot("Value",legend=True)
plt.title('Mortalité en 2005')
plt.legend()
plt.show()