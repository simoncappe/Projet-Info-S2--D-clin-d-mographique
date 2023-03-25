import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import geopandas
from shapely.geometry import Point, LineString, Polygon, MultiPolygon


dep = pd.read_json("tl3_fr.json")
Names_dep = []
Id_dep = []
G_dep = []


for i in dep["features"]:
    Names_dep.append(i["properties"]["nom"])
    Id_dep.append(i["properties"]["code"])

    if i["geometry"]["type"] == "Polygon":
        coords_dep = i["geometry"]["coordinates"][0]
        G_dep.append(Polygon(coords_dep))

    else:
        coords_dep = [Polygon(p[0]) for p in i["geometry"]["coordinates"]]
        G_dep.append(MultiPolygon(coords_dep))


dep_pd = pd.DataFrame(Names_dep, columns=["Departements"])
dep_pd["Id_dep"] = Id_dep


geo_dep = geopandas.GeoDataFrame(dep_pd, geometry=G_dep)


df_dep = pd.read_csv(
    "data_tl3_fr.csv",
    usecols=[
        "TL",
        "REG_ID",
        "Région",
        "Indicateur",
        "SEX",
        "Genre",
        "POS",
        "Année",
        "Value",
    ],
)


### Histogramme des décès d'hommes en fonction des années
annee_mort = {}

df_total = df_dep[
    (
        (df_dep["Indicateur"] == "    Décès, groupe jeunes (0-14)")
        | (df_dep["Indicateur"] == "    Décès, groupe âge actif (15-64)")
        | (df_dep["Indicateur"] == "    Décès, groupe âgé (65+)")
        | (df_dep["Indicateur"] == "      Décès, 80+")
    )
    & (df_dep["Genre"] == "Hommes")
    & (df_dep["Région"] == "France")
]

for indice in range(len(df_total["Année"])):
    annee = df_total["Année"].iloc[indice]
    if f"{annee}" not in annee_mort.keys():
        annee_mort[annee] = df_total["Value"].iloc[indice]
    else:
        annee_mort[annee] += df_total["Value"].iloc["indice"]

# plt.hist(annee_mort.keys(), weights=annee_mort.values())
# plt.show()


### Histogramme des décès en 2005 en fonction de l'âge
tranches_age = {}

df_age = df_dep[
    (df_dep["Région"] == "France")
    & (df_dep["Année"] == 2005)
    & (df_dep["SEX"] == "T")
    & (df_dep["Indicateur"] != "    Décès, groupe jeunes (0-14)")
    & (df_dep["Indicateur"] != "    Décès, groupe âge actif (15-64)")
    & (df_dep["Indicateur"] != "    Décès, groupe âgé (65+)")
    & (df_dep["Indicateur"] != "    Décès, Tous âges")
].reset_index(drop=True)

i = -5
for indice in range(len(df_age["Indicateur"])):
    tranches_age[f"{i}"] = df_age["Value"].iloc[indice]
    i += 5
tranches_age["80"] = tranches_age["-5"]
del tranches_age["-5"]

print(tranches_age)

x = [int(k) for k in tranches_age.keys()]
print(x)

plt.hist(x, weights=tranches_age.values(), orientation="horizontal")
plt.show()
