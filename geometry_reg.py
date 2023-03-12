import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import geopandas
from shapely.geometry import Point, LineString, Polygon, MultiPolygon







df=pd.read_csv('regiondemographique.csv',usecols=['REG_ID', 'Région', 
       'Indicateur', 'SEX', 'Genre', 'POS','Année','Value'])

#regiondemographique.csv est une exportation du site de l'OCDE que j'ai effectuée

df=df[(df.Indicateur==df['Indicateur'][0]) & (df.Année==2005)&(df.SEX=='T') ].iloc[0:8]
#Je veux le Taux de mortalité régional en 2005 pour les hommes ET les femmes (il existe des données différenciées)

g=pd.read_json('geometry.json')
#Fichier sencé contenir les frontières de toute les régions de France, à explorer
g=g.iloc[0:12]



#Le fichier json contient des dictionnaires avec des types Polygon ou Multipolygon
#et puis les coordonnées correspondantes
#Je ne comprend pas trop comment fonctionne les multipolygon pour l'instant mais on 
#arrive à faire quelques trucs en utilisant seulement les polygon, qui nous donnent 
#des frontières acceptables
Poly=[]
MultiPoly=[]
for i in g['features']: 
    if i['geometry']['type']=='Polygon':
        Poly+=i['geometry']['coordinates']
    else:
        MultiPoly+=i['geometry']['coordinates'][0]
G=[]
for i in Poly:
    G.append(Polygon(i))


gpd=geopandas.GeoDataFrame(df,geometry=G)
gpd.plot("Value",legend=True)
plt.title('Taux de mortalité (décès pour 1000 habitants)')
plt.legend()
#Une carte incomplète mais une piste en plus
plt.show()
    


