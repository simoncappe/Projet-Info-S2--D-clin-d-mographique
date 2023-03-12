import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import geopandas
from shapely.geometry import Point, LineString, Polygon



"""
sdmx_query = "REGION_DEMOGR/1+1_PU+1_IN+1_PR+1_PRC+1_PRR.FRA.SURF+POP_DEN+POP_DEN_GR+POP_TYPO_SH+SURF_TYPO_SH+YOU_DEP_RA+ELD_DEP_RA+DEM_DEP_RA+SR_TOT_RA+SR_YOU_RA+SR_ELD_RA+POP_65M_SH+POP_80M_SH+KID_WOM_RA+POP_TOT_GI+POP_65M_GI+DEATH_RA+YOU_DEATH_RA+STD_MORT+INF_MORT+INF_SEXDIF+LIFE_EXP+LIFE_SEXDIF+INMOB_ALL+INMOB_15_29+OUTMOB_ALL+NETMOB_ALL+NETMOB_15_29+FLOWMOB_ALL_RA+NETMOB_ALL_RA+YOUNGMOB_SH.T+F+M.ALL.2005+2006+2007+2008+2009+2010+2011+2012+2013+2014+2015+2016+2017+2018+2019+2020+2021/all?"
data = pd.read_csv(f"https://stats.oecd.org/SDMX-JSON/data/{sdmx_query}&contentType=csv")
print(data)
"""

data_france = pd.read_csv("donnees_outremer_2019/base-ic-evol-struct-pop-2019-com.csv", sep=";", usecols=["IRIS", "COM", "P19_POP"])
data_france = data_france.iloc[:5]
data_france['Latitude'] = [0, 10, 20, 30, 40]
data_france['Longitude'] = [0, -10, 10, 5, 20]
#data_france['Area'] = []

print(data_france)

world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))


def square(x, y):
    return Polygon([(x+1, y+1), (x-1, y+1), (x-1, y-1), (x+1, y-1)])


L=[square(data_france['Longitude'][i], data_france['Latitude'][i])
   for i in range(len(data_france['Longitude']))]



gdf = geopandas.GeoDataFrame(data_france, geometry=L)

gdf['Shape'] = L

print(gdf)

gdf.plot("P19_POP", legend = True)
plt.show()