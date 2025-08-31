# -*- coding: utf-8 -*-
"""
Created on Thu Aug 28 10:58:24 2025

@author: Toonzombie
"""
#Importing libraries

#Basic
import numpy as np
import pandas as pd
import io
import requests

#Graphing
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import folium

#Dashboarding
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go

#Import data
filePath = "./vgsales.csv"
vgsales = pd.read_csv(filePath)
vgsales['Year'] = vgsales['Year'].astype('Int64')
regions = ['NA_Sales','EU_Sales','JP_Sales','Other_Sales', 'Global_Sales']
years = vgsales['Year'].sort_values(ascending=True).dropna().unique()
total_games = vgsales['Name'].count()
statistics_options = ['Platform', 'Year', 'Genre', 'Publisher', 'Sales']
colors = (px.colors.qualitative.Light24 +
           px.colors.qualitative.Dark24 +
           px.colors.qualitative.Alphabet)
app = dash.Dash(__name__)

app.layout = html.Div(children = [html.H1("Video Game Sales Statistics",
                                          style = {'textAlign': 'center', 'font-size': 30}),
                                  html.Div([
                                      html.Div([html.H2("Statistics"),dcc.Dropdown(statistics_options, id = 'input-statistics', value = np.random.choice(statistics_options), style = {'width': 160,'font-size': 25})]),
                                      html.Div([html.H2(id = 'options-title'),dcc.Dropdown(id = 'input-option', value = 'All' ,style = {'width': 256,'font-size': 20})])],
                                      style={'display': 'flex', 'gap': '20px'}),
                                      html.Br(),
                                      html.Div(html.H1(id = 'graphs-title', style={'textAlign': 'center'})),
                                      html.Br(),
                                      html.Div([
                                      html.Div(dcc.Graph(id = 'plot-1')),
                                      html.Div(dcc.Graph(id = 'plot-2'))],
                                      style={'display': 'flex', 'gap': '20px'}),
                                      html.Br(),
                                      html.Br(),
                                      html.Div([
                                      html.Div(dcc.Graph(id = 'plot-3')),
                                      html.Div(dcc.Graph(id = 'plot-4'))],
                                      style={'display': 'flex', 'gap': '20px'})
                                      ]
                    )

@app.callback(
        [Output(component_id='options-title',component_property='children'),
         Output(component_id='input-option',component_property='options'),
         Output(component_id='input-option',component_property='value')],
        [Input(component_id='input-statistics', component_property='value')]
)
def update_options(selected_statistics):
    if selected_statistics != 'Sales' and selected_statistics != 'Publisher':
        options = vgsales[selected_statistics].dropna().unique()
        options = sorted(options) 
        optionsList = [{'label':'All','value':'All'}] + [{'label': option, 'value': option} for option in options]
    elif selected_statistics == 'Sales':
        options = regions
        options = sorted(options) 
        optionsList = [{'label': str(option), 'value': str(option)} for option in options]
    elif selected_statistics == 'Publisher':
        options = vgsales.groupby('Publisher')['Name'].count().nlargest(20)
        options = sorted(options.keys())
        optionsList = [{'label': str(option), 'value': str(option)} for option in options]
    random_value = np.random.choice(options)
    return selected_statistics, optionsList, random_value 

def platform_statistics(input_option):
    if input_option != 'All':
        #Data
        df = vgsales[vgsales['Platform'] == input_option]
        #Fig 1
        df_year = df.groupby(['Year'])['Name'].count().reset_index()
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(x=df_year['Year'], y= df_year['Name'], marker_color=colors))
        fig1.update_layout(title_text = 'Amount of games with over 100,000 copies sold by year', title_x = 0.5)
        #Fig 2
        df_genre = df.groupby(['Genre'])['Name'].count().reset_index()
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=df_genre['Genre'], y= df_genre['Name'], marker_color=colors))
        fig2.update_layout(title_text = 'Amount of games with over 100,000 copies sold per genre', title_x = 0.5)
        #Fig 3
        df_publisher = df.groupby(['Publisher'])['Name'].count().reset_index().sort_values(by = 'Name', ascending = False)
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(x=df_publisher['Publisher'], y= df_publisher['Name'], marker_color=colors))
        fig3.update_layout(title_text = 'Amount of games with over 100,000 copies sold per publisher', title_x = 0.5)
        #Fig 4
        df_sales = df[['NA_Sales','EU_Sales','JP_Sales','Other_Sales', 'Global_Sales']].sum().reset_index()
        df_sales.columns = ['Region', 'Sales']
        fig4 = go.Figure()
        fig4.add_trace(go.Bar(x=df_sales['Region'], y= df_sales['Sales'], marker_color=colors))
        fig4.update_layout(title_text = 'Sales in millions by region', title_x = 0.5)
    return fig1, fig2, fig3, fig4
    
def year_statistics(input_option):
    if input_option != 'All':
        df = vgsales[vgsales['Year'] == input_option]
        #Fig 1
        df_platform = df.groupby(['Platform'])['Name'].count().nlargest(5).reset_index()
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(x=df_platform['Platform'], y= df_platform['Name'], marker_color=colors))
        fig1.update_layout(title_text = 'Amount of games with over 100,000 copies sold for the top 5 platforms in that year', title_x = 0.5)
        #Fig 2
        df_genre = df.groupby(['Genre'])['Name'].count().nlargest(5).reset_index()
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=df_genre['Genre'], y= df_genre['Name'], marker_color=colors))
        fig2.update_layout(title_text = 'Distribution of games with over 100,000 copies sold per genre in that year', title_x = 0.5)
        #Fig 3
        df_publisher = df.groupby(['Publisher'])['Name'].count().nlargest(5).reset_index().sort_values(by = 'Name', ascending = False)
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(x=df_publisher['Publisher'], y= df_publisher['Name'], marker_color=colors))
        fig3.update_layout(title_text = 'Distribution of games with over 100,000 copies sold per publisher in that year', title_x = 0.5)
        #Fig 4
        df_sales = df[['NA_Sales','EU_Sales','JP_Sales','Other_Sales', 'Global_Sales']].sum().reset_index()
        df_sales.columns = ['Region', 'Sales']
        fig4 = go.Figure()
        fig4.add_trace(go.Bar(x=df_sales['Region'], y= df_sales['Sales'], marker_color=colors))
        fig4.update_layout(title_text = 'Sales in millions by region', title_x = 0.5)
    return fig1, fig2, fig3, fig4

def genre_statistics(input_option):
    if input_option != 'All':    
        df = vgsales[vgsales['Genre'] == input_option]
        #Fig 1
        df_platform = df.groupby(['Platform'])['Name'].count().reset_index()
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(x=df_platform['Platform'], y= df_platform['Name'], marker_color=colors))
        fig1.update_layout(title_text = f"Amount of {input_option} games with over 100,000 copies sold by platform", title_x = 0.5)
        #Fig 2
        df_year = df.groupby(['Year'])['Name'].count().reset_index()
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=df_year['Year'], y= df_year['Name'], marker_color=colors))
        fig2.update_layout(title_text = f"Amount of {input_option} games with over 100,000 copies sold per year", title_x = 0.5)
        #Fig 3
        df_publisher = df.groupby(['Publisher'])['Name'].count().reset_index().sort_values(by = 'Name', ascending = False)
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(x=df_publisher['Publisher'], y= df_publisher['Name'], marker_color=colors))
        fig3.update_layout(title_text = 'Distribution of games with over 100,000 copies sold per publisher in that year', title_x = 0.5)
        #Fig 4
        df_sales = df[['NA_Sales','EU_Sales','JP_Sales','Other_Sales', 'Global_Sales']].sum().reset_index()
        df_sales.columns = ['Region', 'Sales']
        fig4 = go.Figure()
        fig4.add_trace(go.Bar(x=df_sales['Region'], y= df_sales['Sales'], marker_color=colors))
        fig4.update_layout(title_text = 'Sales in millions by region', title_x = 0.5)
    return fig1, fig2, fig3, fig4

def publisher_statistics(input_option):
    if input_option != 'All':    
        df = vgsales[vgsales['Publisher'] == input_option]
        #Fig 1
        df_platform = df.groupby(['Platform'])['Name'].count().reset_index()
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(x=df_platform['Platform'], y= df_platform['Name'], marker_color=colors))
        fig1.update_layout(title_text = f"Amount of {input_option} games with over 100,000 copies sold by platform", title_x = 0.5)
        #Fig 2
        df_year = df.groupby(['Year'])['Name'].count().reset_index()
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=df_year['Year'], y= df_year['Name'], marker_color=colors))
        fig2.update_layout(title_text = f"Amount of {input_option} games with over 100,000 copies sold per year", title_x = 0.5)
        #Fig 3
        df_genre = df.groupby(['Genre'])['Name'].count().reset_index().sort_values(by = 'Name', ascending = False)
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(x=df_genre['Genre'], y= df_genre['Name'], marker_color=colors))
        fig3.update_layout(title_text = 'Distribution of games with over 100,000 copies sold per publisher in that year', title_x = 0.5)
        #Fig 4
        df_sales = df[['NA_Sales','EU_Sales','JP_Sales','Other_Sales', 'Global_Sales']].sum().reset_index()
        df_sales.columns = ['Region', 'Sales']
        fig4 = go.Figure()
        fig4.add_trace(go.Bar(x=df_sales['Region'], y= df_sales['Sales'], marker_color=colors))
        fig4.update_layout(title_text = 'Sales in millions by region', title_x = 0.5)
    return fig1, fig2, fig3, fig4
def sales_statistics(input_option):
    if input_option != 'All':    
        df = vgsales[vgsales['Publisher'] == input_option]
        #Fig 1
        df_platform = df.groupby(['Platform'])['Name'].count().reset_index()
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(x=df_platform['Platform'], y= df_platform['Name'], marker_color=colors))
        fig1.update_layout(title_text = f"Amount of {input_option} games with over 100,000 copies sold by platform", title_x = 0.5)
        #Fig 2
        df_year = df.groupby(['Year'])['Name'].count().reset_index()
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=df_year['Year'], y= df_year['Name'], marker_color=colors))
        fig2.update_layout(title_text = f"Amount of {input_option} games with over 100,000 copies sold per year", title_x = 0.5)
        #Fig 3
        df_genre = df.groupby(['Genre'])['Name'].count().reset_index().sort_values(by = 'Name', ascending = False)
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(x=df_genre['Genre'], y= df_genre['Name'], marker_color=colors))
        fig3.update_layout(title_text = 'Distribution of games with over 100,000 copies sold per publisher in that year', title_x = 0.5)
        #Fig 4
        df_sales = df[['NA_Sales','EU_Sales','JP_Sales','Other_Sales', 'Global_Sales']].sum().reset_index()
        df_sales.columns = ['Region', 'Sales']
        fig4 = go.Figure()
        fig4.add_trace(go.Bar(x=df_sales['Region'], y= df_sales['Sales'], marker_color=colors))
        fig4.update_layout(title_text = 'Sales in millions by region', title_x = 0.5)
    return fig1, fig2, fig3, fig4


@app.callback(
        [Output(component_id ='graphs-title', component_property= 'children'),
         Output(component_id='plot-1', component_property='figure'),
         Output(component_id='plot-2', component_property='figure'),
         Output(component_id='plot-3', component_property='figure'),
         Output(component_id='plot-4', component_property='figure')],
        [Input(component_id='input-statistics', component_property='value'),
         Input(component_id='input-option', component_property='value')])
def get_graphs(input_statistics, input_option):
    title = str(input_option) if input_option is not None else "Select an option"
    if input_statistics == 'Platform':
        fig1, fig2, fig3, fig4 = platform_statistics(input_option)        
        
    elif input_statistics == 'Year':
        fig1, fig2, fig3, fig4 = year_statistics(input_option)
    elif input_statistics == 'Genre':
        fig1, fig2, fig3, fig4 = genre_statistics(input_option)
    elif input_statistics == 'Publisher':
        fig1, fig2, fig3, fig4 = publisher_statistics(input_option)
    elif input_statistics == 'Sales':
        fig1, fig2, fig3, fig4 = sales_statistics(input_option)
    else:
        return {}, {}, {}, {}, {}
    return title, fig1, fig2, fig3, fig4
if __name__ == '__main__':
    app.run_server(debug=True)