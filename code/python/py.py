import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import geopandas
from shapely.geometry import Point, LineString, Polygon, MultiPolygon
import plotly.express as px

data = pd.read_csv('data\data_csv\data_tl3_jpan.csv', usecols=['TL', 'REG_ID', 'Région',
                                                               'Indicateur', 'SEX', 'Genre', 'POS', 'Année', 'TIME', 'Value'])

df = data[(data.TL == 3) & (data.SEX == 'T') & (
    data.TIME == 2006)].reset_index(drop=True)


data = data[(data.TL == 3) & (data.SEX == 'T') & (
    data.REG_ID == 'JPA01')].reset_index(drop=True)

j = '    Population, groupe jeune (0-14)'
a = '    Population, groupe d\'âge actif (15-64)'
v = '    Population, groupe âgé (65+)'
t = '  Population, Tous âges'

# data = data[(data.Indicateur != j) & (data.Indicateur != a) & (data.Indicateur != v)&(data.Indicateur!=t)].reset_index(drop=True)
data = data[(data.Indicateur == j) | (data.Indicateur == a)
            | (data.Indicateur == v)].reset_index(drop=True)
L = []

for i in range(len(data['TIME'])):
    n = data['Value'][i]
    d = np.sum(data[data.TIME == data['TIME'][i]]['Value'], axis=0)
    L.append(n/d)
data['Share'] = L


fig = px.histogram(data,
                   x="TIME",
                   y="Value",
                   color="Indicateur",
                   barmode="stack", nbins=23)
#fig.update_xaxes(type='category')
fig.show()




g = pd.read_json("data\geometry\Tl3_jpan.json")
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


















"""data = pd.read_csv('mobility-intern_fr_tl3.csv', usecols = ['TL', 'Région', 'Indicateur','SEX', 'Genre', 'TIME', 'Année','Value'])



indi=data['Indicateur'][0]
print(indi)
df=data[(data.Indicateur==indi)&(data.TL == 3)& (data.SEX == 'T')&(data.Année == 2018)&(data.Value>0)]

df = df.reset_index(drop=True)
print(df)



L=[]
N=[1 for k in range(96)]
R=[[0,0] for i in range(96)]

u=df['Région']
p=len(u)
for i in range (p):
    r=df['Région'][i]
    k=0
    n=len(L)
    while (k<n and r!=L[k]):
        k+=1
    if k==n:
        L.append(r)
        R[k][0]=i
    else:
        N[k]+=1
        R[k][1]=i
    
    
print(len(L))
print('__________')
print(N)
print(R)

print(df.iloc[4])
print('________')
print(df.iloc[39])"""
