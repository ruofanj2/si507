import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from datetime import datetime, timedelta, datetime, date
import plotly.graph_objects as go
import plotly.figure_factory as ff
import plotly.express as px
import pandas as pd
import numpy as np
import json
import os
from urllib.request import urlopen
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)
import requests


def open_cache():
    try:
        data_file_path = os.path.join(os.path.dirname(__file__), CACHE_FILENAME)
        fw = open(data_file_path, 'r')
        cache_dict = json.load(fw)
        fw.close()
    except:
        cache_dict = {}
    return cache_dict

def save_cache(cache_dict):
    data_file_path = os.path.join(os.path.dirname(__file__), CACHE_FILENAME)
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(data_file_path, 'w')
    fw.write(dumped_json_cache)
    fw.close()

def construct_state_unique_key(date, state):
    unique_key = date + state
    return unique_key

def construct_county_unique_key(date, county):
    unique_key = date + county
    return unique_key

app = dash.Dash(__name__)
os.chdir(os.path.dirname(os.path.abspath(__file__)))

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
        
class COVIDStateVaccination:
    
    def __init__(self, index, json):
        self.date = json[index]['date']
        self.state = json[index]['location']
        #AL1D presented as percentage of population with at least 1 dose
        self.AL1D = json[index]['administered_dose1_pop_pct']
        #FV presented as percentage of population with full vaccination
        self.FV = json[index]['series_complete_pop_pct']
        #oneBooster presented as percentage of people who completed a primary series and have received a booster (or additional) dose.
        self.oneBooster = json[index]['additional_doses_vax_pct']
        #secBooster presented as percentage of people ages 50+ with a first booster dose who received a second booster dose based on the jurisdiction where recipient lives
        self.secBooster = json[index]['second_booster_50plus_vax_pct']


#get date of graph1
CACHE_FILENAME = "StateVaccinationCache.json"
APIToken = 'FekNPmDJprQejuDJPUPHGtHVx'
graph1URL = "https://data.cdc.gov/resource/unsk-b7fc.json" + '?$limit=5000' + "&$$app_token=" + APIToken
graph1Data = requests.get(graph1URL).json()
VaccinationStateCache = open_cache()
vaccinationStateData = []
for i in range(len(graph1Data)):
    stateinfo = COVIDStateVaccination(i, graph1Data)
    vaccinationStateData.append(stateinfo)
    uniqkey = construct_state_unique_key(stateinfo.date, stateinfo.state)
    if uniqkey not in VaccinationStateCache.keys():
        VaccinationStateCache[uniqkey] = {'date': stateinfo.date, 'state': stateinfo.state, 'FV': stateinfo.FV, 'AL1D': stateinfo.AL1D, 
                                          '1B': stateinfo.oneBooster, '2B': stateinfo.secBooster}
save_cache(VaccinationStateCache)


#used for date slider
graph1_date = []
for info in vaccinationStateData:
    if info.date[:10] not in graph1_date: 
        graph1_date.append(info.date[:10])
mytotaldates_graph1 = {i:datetime.strptime(x, "%Y-%m-%d").date() for i,x in enumerate(graph1_date)}
graph1_index = (list(mytotaldates_graph1.keys()))


#get graph2 data
CACHE_FILENAME = "CountyVaccinationCache.json"
graph2URL = "https://data.cdc.gov/resource/8xkx-amqh.json" + '?$limit=50000' + "&$$app_token=" + APIToken
graph2Data = requests.get(graph2URL).json()
VaccinationCountyCache = open_cache()
for i in range(len(graph2Data)):
    if (graph2Data[i]["fips"] == 'UNK') or ("series_complete_pop_pct" not in graph2Data[i].keys()) or ("administered_dose1_pop_pct" not in graph2Data[i].keys()):
        continue
    uniqkey = construct_state_unique_key(graph2Data[i]["date"], graph2Data[i]["fips"])
    if uniqkey not in VaccinationCountyCache.keys():
        VaccinationCountyCache[uniqkey] = {'date': graph2Data[i]["date"], 'fips': graph2Data[i]["fips"], 'FV': graph2Data[i]["series_complete_pop_pct"], 
                                        'AL1D': graph2Data[i]["administered_dose1_pop_pct"], '1B': graph2Data[i]["booster_doses_vax_pct"], 
                                        '2B': graph2Data[i]["second_booster_50plus_vax_pct"], 'state': graph2Data[i]["recip_state"], 
                                        "county": graph2Data[i]["recip_county"]}
save_cache(VaccinationCountyCache)
graph2Data = pd.read_json(json.dumps(graph2Data))
graph2Data = graph2Data.loc[graph2Data['fips'] != 'UNK']
graph2Data.replace("", 0)
graph2Data['recip_state'] = graph2Data['recip_state'].map(us_state_abbrev)

#get graph3 data
graph3_4_data = pd.read_csv("United_States_COVID-19_County_Level_of_Community_Transmission_as_Originally_Posted_-_ARCHIVED.csv")
graph3_4_data = graph3_4_data.loc[graph3_4_data['cases_per_100K_7_day_count_change'] != 'suppressed']
graph3_4_data['cases_per_100K_7_day_count_change'] = graph3_4_data['cases_per_100K_7_day_count_change'].str.replace(',','')


app.layout = html.Div(children=[
    html.H1(children = 'US COVID-19 DATA TRACK',
            style = {'text-align':'center'}),
    #varaibles for graph1
    html.Div(children =[
        html.H2(children = 'Graph1: US state Map Colored By Vaccination %',
                style = {'text-align':'center'}),
        #input 1
        dcc.RadioItems(
        id = 'vaccinationOption',
        options=[
            {'label': 'Fully Vaccinated', 'value': 'FV'},
            {'label': 'At least 1 dose', 'value': 'AL1D'},
            {'label': 'Fully Vaccinated with one booster', 'value': '1B'},
            {'label': 'Fully Vaccinated with two booster with age 50+', 'value': '2B'},
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
            min=graph1_index[0],
            max=graph1_index[-1],
            value=graph1_index[0],
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
                for i in np.sort(graph2Data['recip_state'].unique())
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
            {'label': 'Fully Vaccinated with one booster', 'value': '1B'},
            {'label': 'Fully Vaccinated with two booster with age 50+', 'value': '2B'},
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
    html.Hr(),
    #variables for graph3
        #input 7
        dcc.RangeSlider(
            id = 'Dateslider_graph3_4',
        ),
        html.Div(id='output-container-range-slider'),
        html.H2('Graph3: Daily % Positivity - 7-Day Moving Average',
                style = {'text-align':'center'}),
        #graph 3
        dcc.Graph(id = '7_day_moving_Daily_positive'),
    #variables for graph4
        html.H2('Graph4: Daily Cases - 7-Day Moving Average',
                 style = {'text-align':'center'}),
        #graph 4
        dcc.Graph(id = '7_day_moving_Daily_cases')
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
    new_date = str(mytotaldates_graph1[selected_date])
    locationsList = []
    FVlist = []
    AL1Dlist = []
    oneBoosterlist = []
    secondBoosterlist = []
    for info in vaccinationStateData:
        if info.date[:10] == new_date:
            locationsList.append(info.state)
            FVlist.append(float(info.FV))
            AL1Dlist.append(float(info.AL1D))
            oneBoosterlist.append(float(info.oneBooster))
            secondBoosterlist.append(float(info.secBooster))
    if option == 'FV': 
        fig = go.Figure(data=go.Choropleth(
            locations=locationsList, # Spatial coordinates
            z = FVlist, # Data to be color-coded
            locationmode = 'USA-states', # set of locations match entries in `locations`
            colorscale = 'Reds',
            colorbar_title = "Vaccination Rate",
        ))
    elif option == 'AL1D':
        fig = go.Figure(data=go.Choropleth(
        locations=locationsList, # Spatial coordinates
        z = AL1Dlist, # Data to be color-coded
        locationmode = 'USA-states', # set of locations match entries in `locations`
        colorscale = 'Reds',
        colorbar_title = "Vaccination Rate",
    ))
    elif option == '1B':
        fig = go.Figure(data=go.Choropleth(
        locations=locationsList, # Spatial coordinates
        z = oneBoosterlist, # Data to be color-coded
        locationmode = 'USA-states', # set of locations match entries in `locations`
        colorscale = 'Reds',
        colorbar_title = "Vaccination Rate",
    ))
    elif option == '2B':
        fig = go.Figure(data=go.Choropleth(
        locations=locationsList, # Spatial coordinates
        z = secondBoosterlist, # Data to be color-coded
        locationmode = 'USA-states', # set of locations match entries in `locations`
        colorscale = 'Reds',
        colorbar_title = "Vaccination Rate",
    ))
    fig.update_layout(
        title_text = '2022 US vaccination',
        geo_scope='usa', # limite map scope to USA
    )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig

#call back for graph2
@app.callback(
    Output('dropdown-county', 'options'),
    Input('dropdown-state', 'value'))
def set_county_options(selected_state):
    available_county = graph2Data.loc[graph2Data.recip_state == selected_state, 'recip_county'].unique()
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
    available_date = graph2Data.loc[graph2Data.recip_state == selected_state, 'date'].unique()
    dates_graph2 = list(available_date.astype(str))
    mytotaldates_graph2 = {i:datetime.strptime(x[:10], "%Y-%m-%d").date() for i,x in enumerate(dates_graph2)}
    a_graph2 = (list(mytotaldates_graph2.keys()))
    #pdb.set_trace()
    return a_graph2[0]

@app.callback(
    Output('Dateslider_graph2', 'max'),
    Input('dropdown-state', 'value'))
def set_slider_value(selected_state):
    available_date = graph2Data.loc[graph2Data.recip_state == selected_state, 'date'].unique()
    dates_graph2 = list(available_date.astype(str))
    mytotaldates_graph2 = {i:datetime.strptime(x[:10], "%Y-%m-%d").date() for i,x in enumerate(dates_graph2)}
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
    available_date = graph2Data.loc[graph2Data.recip_state == selected_state, 'date'].unique()
    dates_graph2 = list(available_date.astype(str))
    mytotaldates_graph2 = {i:datetime.strptime(x[:10], "%Y-%m-%d").date() for i,x in enumerate(dates_graph2)}
    new_date = str(mytotaldates_graph2[selected_date])
    choosed_county = graph2Data.loc[(graph2Data.recip_state == selected_state)&(graph2Data.date == new_date)]
    #pdb.set_trace()
    if option == 'FV': 
        choosed_county['vaccination rate'] = choosed_county['series_complete_pop_pct'].tolist()
        fig = px.choropleth(choosed_county, geojson=counties, locations='fips', color='vaccination rate',
                           range_color=(0,100),
                           scope="usa",
                           hover_data=["recip_county"],
                           labels={'vaccination':'vaccination'})
    elif option == 'AL1D':
        choosed_county['vaccination rate'] = choosed_county['administered_dose1_pop_pct'].tolist()
        fig = px.choropleth(choosed_county, geojson=counties, locations='fips', color='vaccination rate',
                           range_color=(0, 100),
                           scope="usa",
                           hover_data=["recip_county"],
                           labels={'vaccination':'vaccination'})
    elif option == '1B':
        choosed_county['vaccination rate'] = choosed_county['booster_doses_vax_pct'].tolist()
        fig = px.choropleth(choosed_county, geojson=counties, locations='fips', color='vaccination rate',
                           range_color=(0, 100),
                           scope="usa",
                           hover_data=["recip_county"],
                           labels={'vaccination':'vaccination'})
    elif option == '2B':
        choosed_county['vaccination rate'] = choosed_county['second_booster_50plus_vax_pct'].tolist()
        fig = px.choropleth(choosed_county, geojson=counties, locations='fips', color='vaccination rate',
                           range_color=(0, 100),
                           scope="usa",
                           hover_data=["recip_county"],
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
    available_date = graph2Data.loc[graph2Data.recip_state == selected_state, 'date'].unique()
    dates_graph2 = list(available_date.astype(str))
    mytotaldates_graph2 = {i:datetime.strptime(x[:10], "%Y-%m-%d").date() for i,x in enumerate(dates_graph2)}
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
    Output('7_day_moving_Daily_positive', 'figure'),
    Input('dropdown-state', 'value'),
    Input('dropdown-county', 'value'),
    Input('Dateslider_graph3_4', 'value'),
    )
def update_Daily_figure(selected_state, selected_county, date):
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
    Output('7_day_moving_Daily_cases', 'figure'),
    Input('dropdown-state', 'value'),
    Input('dropdown-county', 'value'),
    Input('Dateslider_graph3_4', 'value'),
    )
def update_Daily_figure(selected_state, selected_county, date):
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

if __name__ == '__main__':
    app.run_server(debug=True)