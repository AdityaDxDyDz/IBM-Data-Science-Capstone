#!/usr/bin/env python
# coding: utf-8

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# 1. Load the SpaceX launch dataset directly from the official IBM cloud storage URL
url = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv"
spacex_df = pd.read_csv(url)

# Get the minimum and maximum payload mass to set up the range slider defaults
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# 2. Initialize the Dash application
app = dash.Dash(__name__)
app.title = "SpaceX Launch Records Dashboard"

# 3. Create the app layout
app.layout = html.Div(children=[
    # Title
    html.H1(
        'SpaceX Launch Records Dashboard',
        style={'textAlign': 'center', 'color': '#503D36', 'font-size': 38, 'margin-bottom': '20px'}
    ),
    
    # TASK 1: Dropdown menu for Launch Site selection
    html.Div([
        html.Label("Select Launch Site:", style={'font-size': 18, 'font-weight': 'bold'}),
        dcc.Dropdown(
            id='site-dropdown',
            options=[
                {'label': 'All Sites', 'value': 'ALL'},
                {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
            ],
            value='ALL',
            placeholder="Select a Launch Site here",
            searchable=True,
            style={'width': '100%', 'padding': '3px', 'font-size': '18px'}
        )
    ], style={'margin-bottom': '30px'}),
    
    # TASK 2: Pie chart for successful launches
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),
    
    # TASK 3: Range Slider for selecting Payload Mass
    html.Div([
        html.Label("Select Payload Mass (kg):", style={'font-size': 18, 'font-weight': 'bold'}),
        dcc.RangeSlider(
            id='payload-slider',
            min=0,
            max=10000,
            step=1000,
            marks={i: f'{i} kg' for i in range(0, 10001, 2500)},
            value=[min_payload, max_payload]
        )
    ], style={'margin-top': '20px', 'margin-bottom': '40px'}),
    
    # TASK 4: Scatter chart for Payload Mass vs. Launch Outcome
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# -------------------------------------------------------------------------
# TASK 2: Callback function to render the Pie Chart based on selected site
# -------------------------------------------------------------------------
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Group by launch site and sum the successful landings (where class == 1)
        fig = px.pie(
            spacex_df, 
            values='class', 
            names='Launch Site', 
            title='Total Successful Launches By All Sites'
        )
        return fig
    else:
        # Filter dataframe for the specific launch site selected
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        # Calculate success (1) vs failure (0) counts for the site
        site_counts = filtered_df['class'].value_counts().reset_index()
        site_counts.columns = ['class', 'count']
        site_counts['Outcome'] = site_counts['class'].map({1: 'Success', 0: 'Failure'})
        
        fig = px.pie(
            site_counts, 
            values='count', 
            names='Outcome', 
            title=f'Total Success vs. Failure Launches for Site {entered_site}',
            color='Outcome',
            color_discrete_map={'Success': '#2ecc71', 'Failure': '#e74c3c'}
        )
        return fig

# -------------------------------------------------------------------------
# TASK 4: Callback function to render the Scatter Chart based on Site & Slider
# -------------------------------------------------------------------------
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    # Filter dataset based on the range slider values
    mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
    range_df = spacex_df[mask]
    
    if entered_site == 'ALL':
        fig = px.scatter(
            range_df, 
            x='Payload Mass (kg)', 
            y='class', 
            color='Booster Version Category',
            title='Correlation Between Payload and Success for All Sites',
            labels={'class': 'Launch Outcome (1=Success, 0=Failure)'},
            hover_data=['Launch Site']
        )
        return fig
    else:
        # Filter further for the specifically selected site
        site_range_df = range_df[range_df['Launch Site'] == entered_site]
        fig = px.scatter(
            site_range_df, 
            x='Payload Mass (kg)', 
            y='class', 
            color='Booster Version Category',
            title=f'Correlation Between Payload and Success for Site {entered_site}',
            labels={'class': 'Launch Outcome (1=Success, 0=Failure)'},
            hover_data=['Booster Version Category']
        )
        return fig

# 4. Run the app
if __name__ == '__main__':
    # Using app.run() instead of app.run_server() to avoid deprecation warnings
    app.run(debug=True, port=8050)
