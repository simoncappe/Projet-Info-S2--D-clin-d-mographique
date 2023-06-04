import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.RangeSlider(
        id='my-range-slider',
        min=0,
        max=100,
        step=1,
        value=[20, 80],  # Valeurs initiales pour la barre de début et la barre de fin
        marks={i: str(i) for i in range(101)},  # Marques affichées sur le slider
    ),
    html.Div(id='slider-output-container')  # Div pour afficher la valeur sélectionnée du slider
])

@app.callback(
    Output('slider-output-container', 'children'),
    Input('my-range-slider', 'value')
)
def update_slider_output(value):
    return f"Barre de début: {value[0]}, Barre de fin: {value[1]}"

if __name__ == '__main__':
    app.run_server(debug=True)

