"""
@author: Blaine Honohan
"""

import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_table
import plotly.express as px
import pandas as pd
import requests

#grab links for first 151 pokemon
pokemon_all_url = "https://pokeapi.co/api/v2/pokemon/?limit=151"

params = {}
pokemon_links = requests.get(pokemon_all_url, params=params).json()
pokemon_links = pokemon_links['results']

#create empty dataframes
pokemon_master = pd.DataFrame(columns=['ID','Name','Type 1','Type 2','Height','Weight','Base Experience','HP','Attack','Defense','Special Attack','Special Defense','Speed','Image Link'])

#loop through 151 links and get data on each individual pokemon
for link in pokemon_links:
    pokemon_url = link['url']
    pokemon_link = requests.get(pokemon_url, params=params).json()
    
    #create empty dictionary to load to data frame
    pokemon = {}
    
    #go through various fields and build pokemon_master data frame
    pokemon['ID'] = pokemon_link['id']
    pokemon['Name'] = pokemon_link['name'].title()
    pokemon['Type 1'] = pokemon_link['types'][0]['type']['name'].title()
    #pokemon may not have a secondary type, prevent errors by using if statement
    if len(pokemon_link['types']) == 2:
        pokemon['Type 2'] = pokemon_link['types'][1]['type']['name'].title()
    pokemon['Height'] = pokemon_link['height']
    pokemon['Weight'] = pokemon_link['weight']
    pokemon['Base Experience'] = pokemon_link['base_experience']
    pokemon['Image Link'] = pokemon_link['sprites']['front_default']
    #loop through stats dictionary
    for stat in pokemon_link['stats']:
        stat_name = stat['stat']['name'].replace("-", " ").title()
        stat_name = stat_name.replace('Hp', 'HP')
        pokemon[stat_name] = stat['base_stat']
    
    #append final dictionary to pokemon_master
    pokemon_master = pokemon_master.append(pokemon, ignore_index=True)

#get unique list of types
type_1 = pd.DataFrame({'Type' : pokemon_master['Type 1']})
type_2 = pd.DataFrame({'Type' : pokemon_master['Type 2']})
pokemon_types = type_1.append(type_2, ignore_index=True)
pokemon_types = pokemon_types.dropna(axis=0, how='any')
pokemon_types = list(pokemon_types['Type'].unique())
pokemon_types.sort()

pokemon_stats = ['Attack', 'Base Experience', 'Defense', 'HP', 'Height', 'Special Attack', 'Special Defense', 'Speed', 'Weight']

pokemon_master['Type 2'] = pokemon_master['Type 2'].fillna(value='NA')

type_1_pie = px.pie(pokemon_master.sort_values(by=['Type 1'], ascending=False), names='Type 1', title='Pokemon Type 1 Pie Chart')
type_2_pie = px.pie(pokemon_master.sort_values(by=['Type 2'], ascending=False), names='Type 2', title='Pokemon Type 2 Pie Chart')

stylesheet = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "20rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

CONTENT_STYLE = {
    "margin-left": "22rem",
    #"margin-right": "2rem",
    "padding": "2rem 1rem",
    "display": "inline-block"
}

sidebar = html.Div(
    [
        html.H2("Filters",
                className="display-4",
                style={'textAlign' : 'center'}
                ),
        html.Hr(),
        html.P(
            'Please apply filters here.',
            className='lead',
            style={'textAlign' : 'center'}
        ),
        html.Br(),
        'Select Pokemon Types (1 or 2):',
        dcc.Dropdown(
            id='type_dropdown',
            options=[{'label' : t, 'value' : t} for t in pokemon_types],
            value=[t for t in pokemon_types],
            multi=True
            ),
        html.Br(),
        'Choose stats for Scatter Plot:',
        html.Br(),
        'X-Axis:',
        dcc.Dropdown(
            id='x_axis_selection',
            options=[{'label' : s, 'value' : s} for s in pokemon_stats],
            value='Attack',
            clearable=False),
        'Y-Axis:',
        dcc.Dropdown(
            id='y_axis_selection',
            options=[{'label' : s, 'value' : s} for s in pokemon_stats],
            value='Defense',
            clearable=False),
    ],
    style=SIDEBAR_STYLE,
)

mainDiv = html.Div([
    html.H1('Gotta Catch \'Em All!  Poke' + u'\u0301' + 'mon Dashboard',
            #style={'textAlign' : 'center'}
            ),
    html.Br(),
    html.Div([
        html.H4('About This Dashboard'),
        '-Since its launch in 1996, Poke' + u'\u0301' + 'mon has become a worldwide sensation!\n',
        html.Br(),
        '-This dashboard is to investigate the original 151 Poke' + u'\u0301' + 'mon.\n',
        html.Br(),
        html.A('-Data was pulled from the Poke' + u'\u0301' + 'API',
               href='https://www.pokeapi.co/',
               target='_blank')
        ]),
    html.Br(),
    html.Div([
        html.H4('Pie Charts by Poke' + u'\u0301' + 'mon Type', className='lead'),
        html.P('Note the Type filter in the sidebar does not affect these charts.  These can be used to better understand the distribution of Poke' + u'\u0301' + 'mon types.',
               style={'font-style' : 'italic'}),
        dcc.Graph(figure=type_1_pie,
                  id='type_1_pie',
                  style={'width' : '75%',
                         'display' : 'inline-block'}),
        dcc.Graph(figure=type_2_pie,
                  id='type_2_pie',
                  style={'width' : '75%',
                         'display' : 'inline-block'}),
        ]
    ),
    html.Br(),
    html.Div([
        html.H4('Scatter Plot by Poke' + u'\u0301' + 'mon Stats', className='lead'),
        html.P('Apply type filter and set axes using filters sidebar.',
               style={'font-style' : 'italic'}),
        dcc.Graph(id='scatter_plot',
                  style={'width' : '75%'})
        ]
    ),
    html.Div([
        html.H4('Data Table', className='lead'),
        html.P('Data table of pokemon shown in Scatter Plot above. Table shows 10 rows at a time.',
               style={'font-style' : 'italic'}),
        html.Div(id='pokemon_table',
                 style={'width' : '75%'}),
        ]
    )
    ],
    style=CONTENT_STYLE)

app.layout = html.Div([sidebar, mainDiv])

server = app.server

@app.callback(
    Output(component_id='pokemon_table', component_property='children'),
    [Input(component_id='type_dropdown', component_property='value')]
)
def update_table(type_dropdown):
    pokemon_table = pokemon_master[(pokemon_master['Type 1'].isin(type_dropdown)) | (pokemon_master['Type 2'].isin(type_dropdown))]
    pokemon_table = pokemon_table.drop(['Image Link'], axis=1)
    return html.Div([
            dash_table.DataTable(data=pokemon_table.to_dict('rows'),
                                 columns=[{'id' : x, 'name' : x} for x in pokemon_table.columns],
                                 page_size=10)
        ]
    )

@app.callback(
    Output('scatter_plot', 'figure'), 
    [Input('x_axis_selection', 'value'), 
     Input('y_axis_selection', 'value'),
     Input('type_dropdown', 'value')])
def generate_chart(x_axis_selection, y_axis_selection, type_dropdown):
    pokemon_filtered = pokemon_master[(pokemon_master['Type 1'].isin(type_dropdown)) | (pokemon_master['Type 2'].isin(type_dropdown))]
    fig = px.scatter(pokemon_filtered, x=x_axis_selection, y=y_axis_selection, color='Type 1', custom_data=['Name','Type 1','Type 2'])
    fig.update_traces(
        hovertemplate="<br>".join([
            "Name: %{customdata[0]}",
            "Type 1: %{customdata[1]}",
            "Type 2: %{customdata[2]}",
            x_axis_selection + ": %{x}",
            y_axis_selection + ": %{y}",
        ])
    )
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
