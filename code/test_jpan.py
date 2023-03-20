import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import geopandas
from shapely.geometry import Point, LineString, Polygon, MultiPolygon

g = pd.read_json("data\geometry\Tl3_jpan.json")
print(g)


Names = []
Id = []
G = []
for i in g['features']:
    Names.append(i['properties']['name'])
    # Id.append(i['properties']['reg'])

    if i['geometry']['type'] == 'Polygon':

        p = i['geometry']['coordinates']
        G.append(Polygon(p[0]))
    else:
        mp = i['geometry']['coordinates']
        s = [Polygon(p[0]) for p in mp]
        G.append(MultiPolygon(s))

d = pd.DataFrame(Names, columns=['Région'], index=np.arange(len(Names)))
# d['Id']=Id

df = pd.read_csv('data\data_csv\data_tl3_jpan.csv', usecols=[
                 'TL', 'REG_ID', 'Région', 'Indicateur', 'SEX', 'Genre', 'TIME', 'Année', 'Value'])
indi = df['Indicateur'][63499]
df = df[(df.TL == 3) & (df.Année == 2005) & (df.SEX == 'T')
        & (df.Indicateur == indi)].reset_index(drop=True)


R = []
for i in df['Région']:
    p = d[d['Région'] == i].index.values[0]
    R.append(G[p])
gpd = geopandas.GeoDataFrame(df, geometry=R)
gpd.plot("Value", legend=True)
plt.title(indi)
plt.legend()
plt.show()
