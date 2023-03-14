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



df=pd.read_csv('regiondemographique.csv',usecols=['REG_ID', 'Région', 
       'Indicateur', 'SEX', 'Genre', 'POS','Année','Value'])

#regiondemographique.csv est une exportation du site de l'OCDE que j'ai effectuée

df=df[(df.Indicateur==df['Indicateur'][0]) & (df.Année==2005)&(df.SEX=='T') ]
#Je veux le Taux de mortalité régional en 2005 pour les hommes ET les femmes (il existe des données différenciées)

R=[]
for i in df['Région']:
    p=d[d['Région']==i].index.values[0]
    R.append(G[p])
gpd=geopandas.GeoDataFrame(df,geometry=R)
gpd.plot("Value")
plt.show()

