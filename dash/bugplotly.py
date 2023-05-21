import geopandas as gpd
import numpy as np
import plotly.express as px

import pandas as pd

import matplotlib.pyplot as plt


data = pd.read_csv('data\/allesclar.csv')[['CODGEO', 'REG', 'DEP', 'LIBGEO',
       'POPINC', 'NETMOB', 'NETNAT', 'NETMIG', 'TIME']]#your path
data = data[data.DEP == '08']
gdpp = gpd.read_file('data\/france\/france.shp')
gpdd = gdpp[gdpp.INSEE_DEP == '08'][  #your path
    ['INSEE_COM', 'INSEE_DEP', 'geometry']]
gdpp = gdpp.rename(columns={'INSEE_COM':'CODGEO'})
geojson_dict = gdpp[['CODGEO', 'geometry']].__geo_interface__#données format GEOJson



def prepare_datamap(i,f):
    '''fonction qui prépare la dataframe à ploter
        i : année initiale
        f : année finale'''
    if i<=f:
        
        L = []
        for p in range(i, f+1):
            L.append(data[data.TIME == p])

        final = L[0][['CODGEO', 'REG', 'DEP','LIBGEO']]



        final['POPINC'] = L[0]['POPINC']
        final['NETNAT'] = L[0]['NETNAT']
        final['NETMOB'] = L[0]['NETMOB']    
        final['NETMIG'] = L[0]['NETMIG']
        final = final.reset_index()
        for p in range(1, len(L)):
            data_frame = L[p].reset_index()
            final['POPINC'] = final['POPINC'] + data_frame['POPINC']
            final['NETNAT'] = final['NETNAT'] +data_frame['NETNAT']
            final['NETMOB'] = final['NETMOB'] + data_frame['NETMOB']
            final['NETMIG'] = final['NETMIG'] + data_frame['NETMIG']

        final = final.reset_index()

        
        '''final['CAUSE'] = np.abs(final[['NETNAT', 'NETMOB', 'NETMIG']]).idxmax(
        axis=1)  # maximum des valeurs absolues des composantes
        def signe(x): return (x > 0) + (x < 0)*(-1)# Si la population a augmenté ou baissé
        final['SGN'] = signe(final['POPINC'])
        final['C'] = np.arange(len(final))
        for index in range(len(final)):
            if final['SGN'][index] == -1:
                if final['CAUSE'][index] == 'NETMOB':
                    final['C'][index] = 'NETMOB -'
                elif final['CAUSE'][index] == 'NETNAT':
                    final['C'][index] = 'NETNAT -'
                else:
                    final['C'][index] = 'NETMIG -'
            else:
                if final['CAUSE'][index] == 'NETMOB':
                    final['C'][index] = 'NETMOB +'
                elif final['CAUSE'][index] == 'NETNAT':
                    final['C'][index] = 'NETNAT +'
                else:
                    final['C'][index] = 'NETMIG +'
        '''

        
        return final

carte = prepare_datamap(2014,2016)



print('labes')

comp = 'NETMIG'
u = gdpp['geometry'].iloc[0].centroid
print('sahit')
fig = px.choropleth_mapbox(
        carte,
        geojson=geojson_dict,
        locations='CODGEO',
        color=comp,
        featureidkey="properties.CODGEO",
        color_continuous_scale="Viridis",
        opacity=0.5,
        labels={comp: comp},
        center={"lon": u.x, "lat": u.y},
        zoom=6
)
print('saha')

fig.show()




