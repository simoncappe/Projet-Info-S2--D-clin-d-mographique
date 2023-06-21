import dash
import dash_core_components as dcc
import dash_html_components as html

# Créer l'application Dash
app = dash.Dash(__name__)

# Définir le contenu de la page de description des variables
description_text = """
# Description des variables

Voici une description des variables utilisées dans l'application :

- Variable 1 : Cette variable représente...
- Variable 2 : Cette variable correspond à...
- Variable 3 : Cette variable mesure...

"""

# Définir la mise en page de l'application
app.layout = html.Div(
    children=[
        dcc.Tabs(
            id="tabs",
            value="tab-data",
            children=[
                dcc.Tab(label="Données", value="tab-data"),
                dcc.Tab(label="Description des variables", value="tab-description"),
                # Ajoutez d'autres onglets si nécessaire
            ],
        ),
        html.Div(id="tab-content"),
    ]
)


@app.callback(
    dash.dependencies.Output("tab-content", "children"),
    [dash.dependencies.Input("tabs", "value")]
)
def render_tab_content(tab):
    if tab == "tab-data":
        # Contenu de l'onglet "Données"
        return html.Div("Contenu de l'onglet Données")
    elif tab == "tab-description":
        # Lien vers la page de description des variables
        return html.A("Voir la description des variables", href="/description", target="_blank")
    # Ajoutez d'autres conditions pour d'autres onglets si nécessaire
    else:
        return html.Div("Contenu de l'onglet non disponible")




# Lancer l'application
if __name__ == "__main__":
    app.run_server(debug=True)
