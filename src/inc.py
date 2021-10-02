import pandas as pd
import json
import plotly
import plotly.express as px
import datetime as dt
from  geopy.geocoders import Nominatim
import meteomatics.api as weather
from src.api_config import *

def get_graphs(city="Toronto", country="Canada"):
    if not city and not country:
        return

    # Heat Stress Time series
    graph1JSON = get_heat_stress_graph(city, country)

    # Graph two
    df = px.data.iris()
    fig2 = px.scatter_3d(df, x='sepal_length', y='sepal_width', z='petal_width',
            color='species',  title="Iris Dataset")
    graph2JSON = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)

    # Graph three
    df = px.data.gapminder().query("continent=='Oceania'")
    fig3 = px.line(df, x="year", y="lifeExp", color='country',  title="Life Expectancy")
    graph3JSON = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)

    return (graph1JSON, graph2JSON, graph3JSON)


def get_heat_stress_graph(city, country):
    df = get_heat_stress_data(city, country)
    fig = px.line(df, x='date', y="value")
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

def get_msg(city=None, country=None):
    DEFAULT = "Please enter your location to obtain a warning"
    if not city and not country:
        msg = DEFAULT
    else:
        msg = f"It is {get_heat_stress_risk(city, country)}."
    return msg


def get_trigger():
    triggers = {"green": "success", "red": "danger", "yellow": "warning"}
    return triggers["green"]


def get_heat_stress_data(city, country):
    geolocator = Nominatim(user_agent="HeatML")
    loc = geolocator.geocode(city +','+ country)
    lat = loc.latitude
    lng = loc.longitude

    curr_dt = dt.datetime.utcnow()
    prev_dt = curr_dt - dt.timedelta(days=10)
    curr_dt = curr_dt +  + dt.timedelta(days=10)
    curr_dt = str(curr_dt.isoformat()) + "Z"
    prev_dt = str(prev_dt.isoformat()) + "Z"
    interval = 6 # hours

    url=f"https://api.meteomatics.com/{prev_dt}--{curr_dt}:PT{interval}H/t_apparent:F/{lat},{lng}/json?model=mix"
    
    df = weather.query_api(url=url, username=USER, password=PASSWORD)
    response = dict(df.json())
    data = response["data"][0]["coordinates"][0]["dates"]
    df = pd.DataFrame(data)

    return df

def get_heat_stress_risk(city, country):


    return "risky"


get_heat_stress_data('Toronto', 'Canada')
