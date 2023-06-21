import dash
from dash import html, dcc

dash.register_page(__name__)


layout = html.Div(children=[
    html.H1(children='Description des variables'),
    html.Ul(id='list',
                                        children=[
                                            html.Li(id='POPINC',
                                                    children="Variation de la Population : Incrément de population au sein de la commune entre le premier Janvier de l\'année initiale et le premier Janvier de l\'année finale"
                                                    ),
                                            html.Li(id="NETNAT",
                                                    children="Solde naturel : Différence entre le nombre de naissances et le nombre de décès enregistrés au sein de la commune entre le premier Janvier de l\'année initiale et le premier Janvier de l\'année finale "
                                                    ),
                                            html.Li(id="NETMOB",
                                                    children="Solde migratoire interne : Différence entre le nombre de personnes ayant emménagé dans la commune qui vivaient déjà en France et le nombre de personne vivant dans la commune et qui ont déménagé autre part en France entre le premier Janvier de l\'année initiale et le premier Janvier de l\'année finale"
                                                    ),
                                            html.Li(id="NETMIG",
                                                    children="Solde migratoire externe : Différence entre le nombre de personnes ayant emménagé dans la commune qui vivaient à l'étranger et le nombre de personnes vivant dans la commune et qui ont déménagé à l'étranger"
                                                    ),
                                            html.Li(id="C",
                                                    children="Cause du changement de population : Maximum en valeur absolue des trois composantes présentées ci-dessus, accompagnée d'un indicateur montrant si la population a augmenté ou diminué"
                                                    )
                                        ]
                                        )
])

if __name__ == "__main__":
    app.run_server(debug=True)


