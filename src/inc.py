import pandas as pd
import json
import plotly
import plotly.express as px
import datetime as dt
from  geopy.geocoders import Nominatim
import meteomatics.api as weather
from src.api_config import *
from scipy import stats


def get_graphs(df):
    # Heat Stress Time series
    graph1JSON = get_heat_stress_graph(df)

    # soil_moisture_deficit:mm	
    graph2JSON = get_soil_moisture_graph(df)

    # Forest Fire index
    graph3JSON = get_fire_index_graph(df)

    #carbon monoxide [μgm3] | o3:ugm3	| no2:ugm3 | oh:pgm3 | t_000m:F | t_2000m:F	
    graph4JSON = get_air_graph(df)

    return (graph1JSON, graph2JSON, graph3JSON, graph4JSON)


def get_heat_stress_graph(df):
    fig = px.line(df, x='Datetime', y="Heat Index (F)", title="Heat Index Time Series")
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


def get_soil_moisture_graph(df):
    df2 = df.rename(columns={"Soil Moisture (mm)": "Soil Moisture Deficit (mm)"})
    fig = px.line(df2, x='Datetime', y="Soil Moisture Deficit (mm)", title="Soil Moisture Deficit Time Series")
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


def get_fire_index_graph(df):
    fig = px.line(df, x='Datetime', y="Forest Fire Index", title="Forest Fire Index Time Series")
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


def get_air_graph(df):
    # fig = px.line(df, x='Datetime', y=["Carbon Monoxide (ugm3)", "Ozone (ugm3)", "Nitrogen Dioxide (ugm3)", "Temp Diff 1km vs 2m (F)"], title="Air Quality Time Series")
    df2 = df.rename(columns={"Carbon Monoxide (ugm3)": "CO (ugm3)", "Ozone (ugm3)": "O3 (ugm3)", "Nitrogen Dioxide (ugm3)": "NO2 (ugm3)"})
    fig = px.line(df2, x='Datetime', y=["CO (ugm3)", "O3 (ugm3)", "NO2 (ugm3)"], title="Air Quality Time Series")
    fig.update_layout(
        yaxis_title="Gas Density (ug/m^3)",
    )
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


def get_msg(df, city, country):
    max_hs = float(get_heat_stress_max(df))
    location = city + ", " + country
    if max_hs < 91:
        msg = f"Predicted low risk for {location}. Practice basic safety and planning. Wear lightweight clothing. Use sunscreen."
    elif max_hs >= 91 and max_hs < 103:
        msg = f"Predicted moderate risk for {location}. Implement precautions and heighten awareness. Drink plenty of fluids, take precautions with certain medications. Take it easy."
    else:
        msg = f"Predicted high risk for {location}. Based on given data, you are not at risk of any heat-related illnesses. Get accilimated and be cautious."
    return msg


def get_trigger(df):
    triggers = {"green": "success", "red": "danger", "yellow": "warning"}
    trigger = None
    max_hs = float(get_heat_stress_max(df))
    if max_hs < 91:
        trigger = triggers["green"]
    elif max_hs >= 91 and max_hs < 103:
        trigger = triggers["yellow"]
    else:
        trigger = triggers["red"]

    return trigger


def get_data(city, country):
    geolocator = Nominatim(user_agent="HeatML")
    loc = geolocator.geocode(city+','+ country)
    lat = loc.latitude
    lng = loc.longitude

    curr_dt = dt.datetime.utcnow()
    prev_dt = curr_dt - dt.timedelta(days=60)
    curr_dt = dt.datetime.utcnow() + dt.timedelta(days=1)
    curr_dt = str(curr_dt.isoformat()) + "Z"
    prev_dt = str(prev_dt.isoformat()) + "Z"
    interval = 6 # hours

    url=f"https://api.meteomatics.com/{prev_dt}--{curr_dt}:PT{interval}H/t_apparent:F,soil_moisture_deficit:mm,forest_fire_warning:idx,co:ugm3,o3:ugm3,no2:ugm3,t_1000m:F,t_2m:F/{lat},{lng}/json?model=mix"
    df = weather.query_api(url=url, username=USER, password=PASSWORD)
    response = dict(df.json())

    data = response["data"]
    apparent, soil, fire, co, o3, no2, t1000, t2 = data
    apparent, soil, fire, co, o3, no2, t1000, t2 = apparent["coordinates"][0]["dates"], soil["coordinates"][0]["dates"], fire["coordinates"][0]["dates"], co["coordinates"][0]["dates"], o3["coordinates"][0]["dates"], no2["coordinates"][0]["dates"], t1000["coordinates"][0]["dates"], t2["coordinates"][0]["dates"]


    df1 = pd.DataFrame(apparent).rename(columns={"value": "Heat Index (F)", "date": "Datetime"})
    df2 = pd.DataFrame(soil).rename(columns={"value": "Soil Moisture (mm)", "date": "Datetime"})
    df3 = pd.DataFrame(fire).rename(columns={"value": "Forest Fire Index", "date": "Datetime"})
    df4 = pd.DataFrame(co).rename(columns={"value": "Carbon Monoxide (ugm3)", "date": "Datetime"})
    df5 = pd.DataFrame(o3).rename(columns={"value": "Ozone (ugm3)", "date": "Datetime"})
    df6 = pd.DataFrame(no2).rename(columns={"value": "Nitrogen Dioxide (ugm3)", "date": "Datetime"})
    df7 = pd.DataFrame(t1000).rename(columns={"value": "Temp @ 1km (F)", "date": "Datetime"})
    df8 = pd.DataFrame(t2).rename(columns={"value": "Temp @ 2m (F)", "date": "Datetime"})
    df = df1
    df["Soil Moisture (mm)"] = df2["Soil Moisture (mm)"]
    df["Forest Fire Index"] = df3["Forest Fire Index"]
    df["Carbon Monoxide (ugm3)"] = df4["Carbon Monoxide (ugm3)"]
    df["Ozone (ugm3)"] = df5["Ozone (ugm3)"]
    df["Nitrogen Dioxide (ugm3)"] = df6["Nitrogen Dioxide (ugm3)"]
    df["Temp Diff 1km vs 2m (F)"] = df7["Temp @ 1km (F)"].subtract(df8["Temp @ 2m (F)"])

    return df


def get_heat_stress_max(df):
    start = str(dt.datetime.utcnow().isoformat()) + "Z"
    range = (df['Datetime'] > start)
    df1 = df.loc[range]
    max_hs = df1["Heat Index (F)"].max()

    return max_hs


def get_stress_graph_stats(df):
    df_tmp = df
    df_tmp["date"] = pd.to_datetime(df_tmp["Datetime"])
    df_tmp['date_ordinal'] = pd.to_datetime(df_tmp['Datetime']).map(dt.datetime.toordinal)
    slope, intercept, r_value, p_value, std_err = stats.linregress(df_tmp['date_ordinal'], df_tmp["Heat Index (F)"])
    return slope, intercept, r_value, p_value, std_err