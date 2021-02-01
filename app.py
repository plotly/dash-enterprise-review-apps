import dash
import dash_html_components as html
import dash_core_components as dcc

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1("hello world"),
    dcc.Graph(figure={'data': [{'x': [1, 2, 3], 'y': [2, 1, 6]}]})
])

if __name__ == "__main__":
    app.run_server(debug=True)
