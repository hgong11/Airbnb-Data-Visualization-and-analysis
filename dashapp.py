import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

df_2020_sep = pd.read_csv('listings_2020_sep.csv.gz', compression='gzip')
df_2019_sep = pd.read_csv('listings_2019_sep.csv.gz', compression='gzip')

df_2020_sep.price.replace('[\$\,]', '', regex=True, inplace = True)
df_2020_sep['price'] = df_2020_sep['price'].astype(float)
df_2019_sep.price.replace('[\$\,]', '', regex=True, inplace = True)
df_2019_sep['price'] = df_2019_sep['price'].astype(float)

df_2020_sep['revenue'] = df_2020_sep['price']*(30-df_2020_sep['availability_30'])
df_2019_sep['revenue'] = df_2019_sep['price']*(30-df_2019_sep['availability_30'])

avg_revenue_2020 = df_2020_sep.groupby('neighbourhood_cleansed')['revenue'].mean().round(decimals=2).reset_index(name='avg_revenue')
avg_revenue_2019 = df_2019_sep.groupby('neighbourhood_cleansed')['revenue'].mean().round(decimals=2).reset_index(name='avg_revenue')

with open('neighbourhoods.geojson') as fp:
    TRT_geo = json.load(fp)

fig_map = px.choropleth_mapbox(avg_revenue_2020, geojson=TRT_geo,
                               locations="neighbourhood_cleansed",
                               featureidkey="properties.neighbourhood",
                               color=avg_revenue_2020['avg_revenue'],
                               color_continuous_scale="Viridis",
                               mapbox_style="carto-positron",
                               zoom=9.5,
                               center={"lat": 43.722275, "lon": -79.366074},
                               opacity=0.5
                               )
fig_map.update_layout(margin={"r":0,"t":0.5,"l":0,"b":0})

app.layout = html.Div(
    children=[
        html.H1(children = 'Toronto Airbnb'),
        dcc.Dropdown(
            id='feature_dropdown',
            options=[
                {'label': 'Room type', 'value': 'room_type'},
                {'label': 'Number of bedrooms', 'value': 'beds'}
            ],
            value='room_type'),
        html.Div([
            dcc.Graph(id='map', figure=fig_map, hoverData=None, className='eight columns'),
            dcc.Graph(id='bar', figure={}, className='four columns')
        ])
    ])


@app.callback(
    Output(component_id='bar', component_property='figure'),
    [Input(component_id='map', component_property='hoverData'),
    Input(component_id='feature_dropdown', component_property='value')]
)
def update_bar_graph(hover_data, feature_chosen):
    if hover_data is None:
        chosen_avg_revenue_2020 = df_2020_sep.groupby(feature_chosen)['revenue'].mean().round(decimals=2).reset_index(
            name='avg_revenue')
        chosen_avg_revenue_2019 = df_2019_sep.groupby(feature_chosen)['revenue'].mean().round(decimals=2).reset_index(
            name='avg_revenue')
    else:
        dff_2020_sep = df_2020_sep.loc[df_2020_sep['neighbourhood_cleansed'] == hover_data['points'][0]['location']]
        dff_2019_sep = df_2019_sep.loc[df_2019_sep['neighbourhood_cleansed'] == hover_data['points'][0]['location']]
        print(hover_data)
        print(feature_chosen)

        chosen_avg_revenue_2020 = dff_2020_sep.groupby(feature_chosen)['revenue'].mean().round(decimals=2).reset_index(name='avg_revenue')
        chosen_avg_revenue_2019 = dff_2019_sep.groupby(feature_chosen)['revenue'].mean().round(decimals=2).reset_index(name='avg_revenue')

    fig_bar = go.Figure(data=[go.Bar(
        name='2019',
        x=chosen_avg_revenue_2019[feature_chosen],
        y=chosen_avg_revenue_2019['avg_revenue'],
        ),
        go.Bar(
            name='2020',
            x=chosen_avg_revenue_2020[feature_chosen],
            y=chosen_avg_revenue_2020['avg_revenue'],
        )
    ])
    return fig_bar


if __name__ == '__main__':
    app.run_server(debug=True)