import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import geopandas
from shapely.geometry import Point, LineString, Polygon, MultiPolygon


g=pd.read_json('geometry.json')

#Fichier sencé contenir les frontières de toute les régions de France, à explorer


Names=[]
Id=[]
G=[]
for i in g['features']:
    Names.append(i['properties']['libgeo'])
    Id.append(i['properties']['reg'])

    if i['geometry']['type']=='Polygon':

        p=i['geometry']['coordinates']
        G.append(Polygon(p[0]))
    else:
        mp=i['geometry']['coordinates']
        s=[Polygon(p[0]) for p in mp]
        G.append(MultiPolygon(s))

Names[6]='Nouvelle-Aquitaine'
Names[2]='Provence-Alpes-Côte d’Azur'
Names[3]='Grand Est'
Names[7]='Centre - Val de Loire'

d=pd.DataFrame(Names,columns=['Région'],index=np.arange(len(Names)))
d['Id']=Id


ggd=geopandas.GeoDataFrame(d,geometry=G)


'''
df=pd.read_csv('regiondemographique.csv',usecols=['REG_ID', 'Région', 
       'Indicateur', 'SEX', 'Genre', 'POS','Année','Value'])

#regiondemographique.csv est une exportation du site de l'OCDE que j'ai effectuée
indi=df['Indicateur'][3]
df=df[(df.Indicateur==indi) & (df.Année==2005)&(df.SEX=='T')]
#Je veux le Taux de mortalité régional en 2005 pour les hommes ET les femmes (il existe des données différenciées)
print(Names)
R=[]
for i in df['Région']:
    p=d[d['Région']==i].index.values[0]
    R.append(G[p])
gpd=geopandas.GeoDataFrame(df,geometry=R)
gpd.plot("Value",legend=True)
plt.title(indi[0:35])
plt.legend()
plt.show()
'''

dep = pd.read_json('geometry_dep.json')

Names_dep = []
Id_dep = []
G_dep = []

test=0

for i in dep['features'] :
    Names_dep.append(i['properties']['nom'])
    Id_dep.append(i['properties']['code'])

    if i['geometry']['type']=='Polygon' :
        coords_dep = i['geometry']['coordinates'][0]
        G_dep.append(Polygon(coords_dep))
        test+=1

    else :
        coords_dep = [Polygon(p) for p in i['geometry']['coordinates'][0]]
        G_dep.append(MultiPolygon(coords_dep))
        test+=1

dep_pd = pd.DataFrame(Names_dep, columns=['Departements'])
dep_pd['Id_dep']=Id_dep


geo_dep = geopandas.GeoDataFrame(dep_pd, geometry=G_dep)

geo_dep.plot()
plt.show()
