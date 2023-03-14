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
        
d=pd.DataFrame(Names,columns=['Nom'])
d['Id']=Id


#gd=geopandas.GeoDataFrame(d,geometry=G)



df=pd.read_csv('regiondemographique.csv',usecols=['REG_ID', 'Région', 
       'Indicateur', 'SEX', 'Genre', 'POS','Année','Value'])

#regiondemographique.csv est une exportation du site de l'OCDE que j'ai effectuée

df=df[(df.Indicateur==df['Indicateur'][0]) & (df.Année==2005)&(df.SEX=='T') ]
df.reset_index()
#Je veux le Taux de mortalité régional en 2005 pour les hommes ET les femmes (il existe des données différenciées)
print(df)


gd=geopandas.GeoDataFrame(df,geometry=G[1:13])

gd.plot("Value",legend=True)
plt.title('Taux de mortalité')
plt.legend()
plt.show()