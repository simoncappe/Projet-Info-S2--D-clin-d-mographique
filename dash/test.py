from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import geopandas as gpd
import pandas as pd
import numpy as np

geo = gpd.read_file('data\geometry\Tl2_fr.json')

df = pd.read_csv('data\data_csv\data_tl2_fr.csv', usecols=['REG_ID', 'Région',
                                             'Indicateur', 'SEX', 'Genre', 'POS', 'Année', 'Value'])

# regiondemographique.csv est une exportation du site de l'OCDE que j'ai effectuée
indi = df['Indicateur'][3]
df = df[(df.Indicateur == indi) & (df.Année == 2005) & (df.SEX == 'T')]

data = df.merge(geo,left_on = 'Région',right_on = 'libgeo',how = 'right')[['libgeo','Value']]

data['A'] = np.random.exponential(80,18)
data['B'] = np.random.exponential(80,18)
data['C'] = np.random.exponential(80,18)

geojson_dict = geo.__geo_interface__#conversion des géométries en format geojson


app = Dash(__name__)

app.layout = html.Div(
    [
        html.H4("MAP"),
        html.P("Select a letter :"),
        dcc.RadioItems(
            id="letter",
            options=["A", "B", "C"],
            value="A",
            inline=True,
        ),
        dcc.Graph(id="graph"),
    ]
)


@app.callback(
    Output("graph", "figure"),
    Input("letter", "value"),
)
def display_choropleth(letter):
    
    
    fig = px.choropleth(
        data,
        geojson=geojson_dict,
        color=letter,
        locations="libgeo",
        featureidkey="properties.libgeo",
        projection="mercator",
        range_color=[0, 200],
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)

