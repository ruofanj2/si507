import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, datetime, date
import plotly.graph_objects as go
import plotly.figure_factory as ff
from dash.dependencies import Input, Output
from urllib.request import urlopen
import json
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)
import pdb

app = dash.Dash(__name__)

#graph1 setting up
graph1_data = pd.read_csv('/Users/ruoooofanj2/Desktop/stat430/ruofanj2/finalproject/COVID-19_Vaccinations_in_the_United_States_Jurisdiction.csv')
dates_graph1 = list(graph1_data['Date'].unique())
mytotaldates_graph1 = {i:datetime.strptime(x, "%m/%d/%Y").date() for i,x in enumerate(dates_graph1)}
a_graph1 = (list(mytotaldates_graph1.keys()))

#graph2 setting up
graph2_data = pd.read_csv('/Users/ruoooofanj2/Desktop/stat430/ruofanj2/finalproject/COVID-19_Vaccinations_in_the_United_States_County.csv', dtype={"FIPS": str})
graph2_data = graph2_data.loc[graph2_data['FIPS'] != 'UNK']
us_state_abbrev = {
    'AL': 'Alabama',
    'AK': 'Alaska',
    'AZ': 'Arizona',
    'AR': 'Arkansas',
    'CA': 'California',
    'CO': 'Colorado',
    'CT': 'Connecticut',
    'DE': 'Delaware',
    'FL': 'Florida',
    'GA': 'Georgia',
    'GU': 'Guam',
    'HI': 'Hawaii',
    'ID': 'Idaho',
    'IL': 'Illinois',
    'IN': 'Indiana',
    'IA': 'Iowa',
    'KS': 'Kansas',
    'KY': 'Kentucky',
    'LA': 'Louisiana',
    'ME': 'Maine',
    'MD': 'Maryland',
    'MA': 'Massachusetts',
    'MI': 'Michigan',
    'MN': 'Minnesota',
    'MS': 'Mississippi',
    'MO': 'Missouri',
    'MT': 'Montana',
    'NE': 'Nebraska',
    'NV': 'Nevada',
    'NH': 'New Hampshire',
    'NJ': 'New Jersey',
    'NM': 'New Mexico',
    'NY': 'New York',
    'NC': 'North Carolina',
    'ND': 'North Dakota',
    'OH': 'Ohio',
    'OK': 'Oklahoma',
    'OR': 'Oregon',
    'PA': 'Pennsylvania',
    'RI': 'Rhode Island',
    'SC': 'South Carolina',
    'SD': 'South Dakota',
    'TN': 'Tennessee',
    'TX': 'Texas',
    'UT': 'Utah',
    'VT': 'Vermont',
    'VA': 'Virginia',
    'WA': 'Washington',
    'WV': 'West Virginia',
    'WI': 'Wisconsin',
    'WY': 'Wyoming',
    'MP':'Northern Mariana Islands', 
    'PW':'Palau', 
    'PR':'Puerto Rico',
    'VI':'Virgin Islands', 
    'DC':'District of Columbia'
}
graph2_data['Recip_State'] = graph2_data['Recip_State'].map(us_state_abbrev)



#graph3&4 setting up
graph3_4_data = pd.read_csv('/Users/ruoooofanj2/Desktop/stat430/ruofanj2/finalproject/United_States_COVID-19_County_Level_of_Community_Transmission_as_Originally_Posted.csv')
graph3_4_data = graph3_4_data.loc[graph3_4_data['cases_per_100K_7_day_count_change'] != 'suppressed']
graph3_4_data['cases_per_100K_7_day_count_change'] = graph3_4_data['cases_per_100K_7_day_count_change'].str.replace(',','')


app.layout = html.Div(children=[
    html.H1(children = 'US COVID-19 DATA TRACK',
            style = {'text-align':'center'}),
    #varaibles for graph1
    html.Div(children =[
        html.H2(children = 'Graph1: US State Map Colored By Vaccination %',
                style = {'text-align':'center'}),
        #input 1
        dcc.RadioItems(
        id = 'vaccinationOption',
        options=[
            {'label': 'Fully Vaccinated', 'value': 'FV'},
            {'label': 'At least 1 dose', 'value': 'AL1D'},
        ],
        value='FV',
        labelStyle={'display': 'inline-block', 'marginTop': '5px'},
        style = {'text-align':'center'},
        ),   
        #graph 1
        dcc.Graph(id='graph1'),
        #input 2
        dcc.Slider(
            id='Dateslider_graph1',
            min=a_graph1[0],
            max=a_graph1[-1],
            value=a_graph1[0],
            ),
        html.Div(id='output-container-range-slider-graph1'),
        ]),
    html.Hr(),
    #variables for graph 2
        html.P('State', className = 'fix_label'),
        dcc.Dropdown(
            id='dropdown-state',
            value='Alabama',
            options = [
                {'label': i, 'value': i}
                for i in np.sort(graph2_data['Recip_State'].unique())
                ],
            ),
        #input 4
        html.P('County',className = 'fix_label'),
        dcc.Dropdown(
            id = 'dropdown-county',
            ),
        html.H2(children = 'Graph2: Selected State Map with County OutlineColored By Vaccination %',
                style = {'text-align':'center'}),  
        #input 5
        dcc.RadioItems(
        id = 'vaccinationOption_graph2',
        options=[
            {'label': 'Fully Vaccinated', 'value': 'FV'},
            {'label': 'At least 1 dose', 'value': 'AL1D'},
        ],
        value='FV',
        labelStyle={'display': 'inline-block', 'marginTop': '5px'},
        style = {'text-align':'center'}
        ),   
        dcc.Graph(id='graph2'),
        #input 6
        dcc.Slider(
            id='Dateslider_graph2',
        ),
        html.Div(id='output-container-range-slider-graph2'),
    #variables for graph3
        #input 7
        dcc.RangeSlider(
            id = 'Dateslider_graph3_4',
        ),
        html.Div(id='output-container-range-slider'),
        html.H2('Graph3: Daily % Positivity - 7-Day Moving Average',
                style = {'text-align':'center'}),
        #graph 3
        dcc.Graph(id = '7_day_moving_daily_positive'),
    #variables for graph4
        html.H2('Graph4: Daily Cases - 7-Day Moving Average',
                 style = {'text-align':'center'}),
        #graph 4
        dcc.Graph(id = '7_day_moving_daily_cases')
])

#callback for graph1
@app.callback(
    Output('output-container-range-slider-graph1', 'children'),
    Input('Dateslider_graph1', 'value'),)
def update_output(value):
    result = str(mytotaldates_graph1[value])
    return 'You have selected "{}"'.format(result)

@app.callback(
    Output('graph1', 'figure'),
    Input('Dateslider_graph1', 'value',),
    Input('vaccinationOption','value',),
    )
def update_figure(selected_date, option):
    #pdb.set_trace()
    date1 = str(mytotaldates_graph1[selected_date])
    new_date = date1[5:7] + '/' + date1[8:] + '/' + date1[:4]
    filtered_df = graph1_data[graph1_data['Date'] == new_date]
    #pdb.set_trace()
    if option == 'FV': 
        fig = go.Figure(data=go.Choropleth(
            locations=filtered_df['Location'], # Spatial coordinates
            z = filtered_df['Series_Complete_Pop_Pct'].astype(float), # Data to be color-coded
            locationmode = 'USA-states', # set of locations match entries in `locations`
            colorscale = 'Reds',
            colorbar_title = "Vaccination Rate",
        ))
    elif option == 'AL1D':
        fig = go.Figure(data=go.Choropleth(
        locations=filtered_df['Location'], # Spatial coordinates
        z = filtered_df['Administered_Dose1_Pop_Pct'].astype(float), # Data to be color-coded
        locationmode = 'USA-states', # set of locations match entries in `locations`
        colorscale = 'Reds',
        colorbar_title = "Vaccination Rate",
    ))
    fig.update_layout(
        title_text = '2021 US vaccination',
        geo_scope='usa', # limite map scope to USA
    )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig

#call back for graph2
@app.callback(
    Output('dropdown-county', 'options'),
    Input('dropdown-state', 'value'))
def set_county_options(selected_state):
    available_county = graph2_data.loc[graph2_data.Recip_State == selected_state, 'Recip_County'].unique()
    available_county.sort()
    return [{'label': i, 'value': i} for i in available_county]

@app.callback(
    Output('dropdown-county', 'value'),
    Input('dropdown-county', 'options'))
def set_county_value(available_options):
    return available_options[0]['value']

@app.callback(
    Output('Dateslider_graph2', 'min'),
    Input('dropdown-state', 'value'))
def set_slider_value(selected_state):
    available_date = graph2_data.loc[graph2_data.Recip_State == selected_state, 'Date'].unique()
    dates_graph2 = list(available_date)
    mytotaldates_graph2 = {i:datetime.strptime(x, "%m/%d/%Y").date() for i,x in enumerate(dates_graph2)}
    a_graph2 = (list(mytotaldates_graph2.keys()))
    #pdb.set_trace()
    return a_graph2[0]

@app.callback(
    Output('Dateslider_graph2', 'max'),
    Input('dropdown-state', 'value'))
def set_slider_value(selected_state):
    available_date = graph2_data.loc[graph2_data.Recip_State == selected_state, 'Date'].unique()
    dates_graph2 = list(available_date)
    mytotaldates_graph2 = {i:datetime.strptime(x, "%m/%d/%Y").date() for i,x in enumerate(dates_graph2)}
    a_graph2 = (list(mytotaldates_graph2.keys()))
    #pdb.set_trace()
    return a_graph2[-1]

@app.callback(Output('Dateslider_graph2', 'value'),
              [Input('Dateslider_graph2', 'min'),
               Input('Dateslider_graph2', 'max')])
def update_slider_example_value(min_value, max_value): 
    return min_value


@app.callback(
    Output('graph2', 'figure'),
    Input('dropdown-state', 'value'),
    Input('vaccinationOption_graph2','value',),
    Input('Dateslider_graph2', 'value',),
    )

def update_graph(selected_state,option,selected_date):
    available_date = graph2_data.loc[graph2_data.Recip_State == selected_state, 'Date'].unique()
    dates_graph2 = list(available_date)
    mytotaldates_graph2 = {i:datetime.strptime(x, "%m/%d/%Y").date() for i,x in enumerate(dates_graph2)}
    date1 = str(mytotaldates_graph2[selected_date])
    new_date = date1[5:7] + '/' + date1[8:] + '/' + date1[:4]
    choosed_county = graph2_data.loc[(graph2_data.Recip_State == selected_state)&(graph2_data.Date == new_date)]
    #pdb.set_trace()
    if option == 'FV': 
        choosed_county['vaccination rate'] = choosed_county['Series_Complete_Pop_Pct'].tolist()
        fig = px.choropleth(choosed_county, geojson=counties, locations='FIPS', color='vaccination rate',
                           range_color=(0,100),
                           scope="usa",
                           hover_data=["Recip_County"],
                           labels={'vaccination':'vaccination'})
    elif option == 'AL1D':
        choosed_county['vaccination rate'] = choosed_county['Administered_Dose1_Pop_Pct'].tolist()
        fig = px.choropleth(choosed_county, geojson=counties, locations='FIPS', color='vaccination rate',
                           range_color=(0, 100),
                           scope="usa",
                           hover_data=["Recip_County"],
                           labels={'vaccination':'vaccination'})
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout()
    return fig


@app.callback(
    Output('output-container-range-slider-graph2', 'children'),
    Input('Dateslider_graph2', 'value'),
    Input('dropdown-state', 'value'),
    )
def update_output(value,selected_state):
    #pdb.set_trace()
    available_date = graph2_data.loc[graph2_data.Recip_State == selected_state, 'Date'].unique()
    dates_graph2 = list(available_date)
    mytotaldates_graph2 = {i:datetime.strptime(x, "%m/%d/%Y").date() for i,x in enumerate(dates_graph2)}
    result = str(mytotaldates_graph2[value])
    return 'You have selected "{}"'.format(result)

#call back for graph3&4

@app.callback(
    Output('Dateslider_graph3_4', 'min'),
    Input('dropdown-state', 'value'),
    Input('dropdown-county', 'value'))
def set_slider_value1(selected_state, selected_county):
    available_date = graph3_4_data.loc[(graph3_4_data.state_name == selected_state) & (graph3_4_data.county_name == selected_county), 'report_date'].unique()
    dates_graph3_4 = list(available_date)
    dates_graph3_4.sort(key = lambda date: datetime.strptime(date, '%Y/%m/%d'))
    mytotaldates_graph3_4 = {i:datetime.strptime(x, "%Y/%m/%d").date() for i,x in enumerate(dates_graph3_4)}
    a_graph3_4 = (list(mytotaldates_graph3_4.keys()))
    #pdb.set_trace()
    return a_graph3_4[0]

@app.callback(
    Output('Dateslider_graph3_4', 'max'),
    Input('dropdown-state', 'value'),
    Input('dropdown-county', 'value'))
def set_slider_value2(selected_state, selected_county):
    available_date = graph3_4_data.loc[(graph3_4_data.state_name== selected_state) & (graph3_4_data.county_name == selected_county), 'report_date'].unique()
    dates_graph3_4 = list(available_date)
    dates_graph3_4.sort(key = lambda date: datetime.strptime(date, '%Y/%m/%d'))
    mytotaldates_graph3_4 = {i:datetime.strptime(x, "%Y/%m/%d").date() for i,x in enumerate(dates_graph3_4)}
    a_graph3_4 = (list(mytotaldates_graph3_4.keys()))
    #pdb.set_trace()
    return a_graph3_4[-1]

@app.callback(Output('Dateslider_graph3_4', 'value'),
              [Input('Dateslider_graph3_4', 'min'),
               Input('Dateslider_graph3_4', 'max')])
def update_slider_example_value1(min_value, max_value): 
    #pdb.set_trace()
    return [min_value,max_value]

@app.callback(
    Output('output-container-range-slider', 'children'),
    Input('Dateslider_graph3_4', 'value'),
    Input('dropdown-state', 'value'),
    Input('dropdown-county', 'value'))
def update_output(value,selected_state,selected_county):
    #pdb.set_trace()
    available_date = graph3_4_data.loc[(graph3_4_data.state_name == selected_state) & (graph3_4_data.county_name == selected_county), 'report_date'].unique()
    dates_graph3_4 = list(available_date)
    dates_graph3_4.sort(key = lambda date: datetime.strptime(date, '%Y/%m/%d'))
    mytotaldates_graph3_4 = {i:datetime.strptime(x, "%Y/%m/%d").date() for i,x in enumerate(dates_graph3_4)}
    result1 = str(mytotaldates_graph3_4[value[0]])
    result2 = str(mytotaldates_graph3_4[value[1]])
    result = [result1,result2]
    #pdb.set_trace()
    return 'You have selected "{}"'.format(result)

@app.callback(
    Output('7_day_moving_daily_positive', 'figure'),
    Input('dropdown-state', 'value'),
    Input('dropdown-county', 'value'),
    Input('Dateslider_graph3_4', 'value'),
    )
def update_daily_figure(selected_state, selected_county, date):
    available_date = graph3_4_data.loc[(graph3_4_data.state_name == selected_state) & (graph3_4_data.county_name== selected_county), 'report_date'].unique()
    dates_graph3_4 = list(available_date)
    dates_graph3_4.sort(key = lambda date: datetime.strptime(date, '%Y/%m/%d'))
    mytotaldates_graph3_4 = {i:datetime.strptime(x, "%Y/%m/%d").date() for i,x in enumerate(dates_graph3_4)}
    range1 = range(date[0],date[1]+1,1)
    list1 = []
    for i in range1:
        list1.append(i)
    date1 = list(map(mytotaldates_graph3_4.get, list1))
    date2 = []
    for i in range(len(date1)):
        transdate = str(date1[i])
        date2.append(transdate.replace('-','/'))
    #pdb.set_trace()
    newdf = graph3_4_data.loc[(graph3_4_data.state_name == selected_state)&(graph3_4_data.county_name == selected_county)&(graph3_4_data.report_date.isin(date2))].sort_values('report_date')
    y_average1 = newdf['percent_test_results_reported_positive_last_7_days'].astype(float)
    #pdb.set_trace()
    fig = go.Figure(data=[go.Scatter(x=date2, y=y_average1)])
    fig.update_layout(yaxis_title="Percentage of Positive cases",
                    xaxis_title="Date")
    return fig
 


@app.callback(
    Output('7_day_moving_daily_cases', 'figure'),
    Input('dropdown-state', 'value'),
    Input('dropdown-county', 'value'),
    Input('Dateslider_graph3_4', 'value'),
    )
def update_daily_figure(selected_state, selected_county, date):
    available_date = graph3_4_data.loc[(graph3_4_data.state_name == selected_state) & (graph3_4_data.county_name == selected_county), 'report_date'].unique()
    dates_graph3_4 = list(available_date)
    dates_graph3_4.sort(key = lambda date: datetime.strptime(date, '%Y/%m/%d'))
    mytotaldates_graph3_4 = {i:datetime.strptime(x, "%Y/%m/%d").date() for i,x in enumerate(dates_graph3_4)}
    range1 = range(date[0],date[1]+1,1)
    list1 = []
    for i in range1:
        list1.append(i)
    date1 = list(map(mytotaldates_graph3_4.get, list1))
    date2 = []
    for i in range(len(date1)):
        transdate = str(date1[i])
        date2.append(transdate.replace('-','/'))
    #pdb.set_trace()
    newdf = graph3_4_data.loc[(graph3_4_data.state_name == selected_state)&(graph3_4_data.county_name == selected_county)&(graph3_4_data.report_date.isin(date2))].sort_values('report_date')
    y_average1 = newdf['cases_per_100K_7_day_count_change'].astype(float)
    #pdb.set_trace()
    fig = go.Figure(data=[go.Scatter(x=date2, y=y_average1)],)
    fig.update_layout(yaxis_title="Number of Positive Cases",
                    xaxis_title="Date")
    return fig
# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options

if __name__ == '__main__':
    app.run_server(debug=True)