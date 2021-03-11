from flask import Flask, jsonify, render_template, request
import csv
import numpy as np
from models import Air, AirSchema
from config import db
import json
from datetime import date, datetime, timedelta
from flask import send_file, send_from_directory, safe_join, abort
import math
import time
from sqlalchemy import func
import matplotlib
from matplotlib import pyplot as plt
print ("Switched to:",matplotlib.get_backend())
import pandas as pd
import matplotlib.dates as mdates
from matplotlib.dates import MO, TU, WE, TH, FR, SA
from flask import Response, redirect, request, url_for
print ("P1")
#----------

#app = connexion.FlaskApp(__name__, specification_dir='./')  # or e.g. Flask(__name__, template_folder='../otherdir')

from config import app


#app = Flask(__name__)
#Talisman(app)

# Read the swagger.yml file to configure the endpoints
#app.add_api('air.yml')

NUM_OF_POLLLUTANTS = 10
NUM_OF_WEATHER_COMP = 4

# RL values
MQ2_RL = 10
MQ4_RL = 20
MQ6_RL = 20
MQ7_RL = 20
MQ131_RL = 10

# Taking initial Cupertino readings as Ro
MQ2_Ref_Ro = 6.69
MQ4_Ref_Ro = 78.02
MQ6_Ref_Ro = 7.01
MQ7_Ref_Ro = 8.22
MQ131_Ref_Ro = 85.71

dust_Voc = 0.03
print ("P2")

MQ2_LPGCurve = [2.3, 0.21, -0.47]
MQ2_COCurve = [2.3, 0.72, -0.34]
MQ2_SmokeCurve = [2.3, 0.53, -0.44]
MQ4_MethaneCurve = [2.254, -0.224, -0.077]
MQ6_LPGCurve = [2.301, 0.307, -0.422]
MQ7_COCurve = [1.699, 0.201, -0.651]
MQ7_H2Curve = [1.699, 0.087, -0.729]
MQ131_O3Curve  = [0.692, 0.608, -0.900]

DAYS = "days"
HOURS = "hours"
ONE_HOUR = 1
ONE_DAY = 1
ONE_WEEK = 7
ONE_MONTH = 30
TWO_MONTH = 60
THREE_MONTH = 90
#TIMESERIES_QUARTER = 90
TIMESERIES_QUARTER = 60
PM25 = "pm25"
tVOC = "tVOC"
CO2 = "co2"
O3 = "o3"
TEMP = "temp"
HUMIDITY = "humidity"
TS_THRESHOLDS_JSON = "ts_thresholds.json"

NAME_PM25 = "Particulate Matter"
ABBR_PM25 = "PM2.5"
UNITS_PM25 = "ug/m3"
ORDER_PM25 = 1
CONTENT_PM25 = '<ul><li>Avoid smoke, burning wood, candles, incense, etc.</li><li>Ventilate and use exhaust fans</li><li>Use exhaust fan while cooking</li><li>Use HEPA filters to purify air</li><li><a href="https://www.airnow.gov/aqi/aqi-basics/extremely-high-levels-of-pm25" target="_blank">Further Reading</a></li></ul><p style="padding-left: 30px;">Thresholds (ug/m3):<br />&bull; Good: 0-12<br />&bull; Average: 12-15<br />&bull; Poor: 15-35<br />&bull; Bad: &gt;35</p>'

NAME_TVOC = "Volatile Organic Compounds"
ABBR_TVOC = "VOC"
UNITS_TVOC = "ppb"
ORDER_TVOC = 2
CONTENT_TVOC = '<ul><li>Ventilate</li><li>Reduce use of spray cosmetics, perfumes, air fresheners, aerosols</li><li>Ventilate while using soaps, cleaning solvents, paints, nail polish removers</li><li><a href="https://thegreendivas.com/2015/06/12/16-ways-to-reduce-exposure-to-off-gassing-vocs-infographic" target="_blank">Further Reading</a></li></ul><p style="padding-left: 30px;">Thresholds (ppb):<br />&bull; Good: 0-220<br />&bull; Average: 221-660<br />&bull; Poor: 661-2000<br />&bull; Bad: &gt;2000</p>'

NAME_CO2 = "Carbon Dioxide"
ABBR_CO2 = "CO2"
UNITS_CO2 = "ppm"
ORDER_CO2 = 3
CONTENT_CO2 = '<ul><li>Ventilate, especially while cooking and in gatherings</li><li>Get houseplants</li><li>Avoid smoke</li><li><a href="https://learn.kaiterra.com/en/air-academy/tips-for-reducing-co2" target="_blank">Further Reading</a></li></ul><p style="padding-left: 30px;">Thresholds (ppm):<br />&bull; Good: 350-1000<br />&bull; Average: 1001-2000<br />&bull; Poor: 2001-5000<br />&bull; Bad: &gt;5000</p>'

NAME_O3 = "Ozone"
ABBR_O3 = "O3"
UNITS_O3 = "ppm"
ORDER_O3 = 4
CONTENT_O3 = '<ul><li>Check your air purifier to see if it adds or removes ozone</li><li>Use activated carbon air filters</li><li>Get houseplants that absorb ozone</li><li><a href="https://www.sciencedaily.com/releases/2009/09/090908103634.htm" target="_blank">Further Reading</a></li></ul><p style="padding-left: 30px;">Thresholds (ppm):<br />&bull; Good: < 0.06<br />&bull; Average: < 0.09<br />&bull; Poor: < 0.20<br />&bull; Bad: &gt;=0.20</p>'

NAME_CO = "Carbon Monoxide"
ABBR_CO = "CO"
UNITS_CO = "ppm"
ORDER_CO = 5
CONTENT_CO = '<ul><li>Ventilate</li><li>Avoid smoke</li><li>Have appliances and heating systems serviced</li><li>Don&rsquo;t run car engine in garage</li><li><a href="https://www.health.harvard.edu/blog/keeping-carbon-monoxide-out-2018012213141" target="_blank">Further Reading</a></li></ul><p style="padding-left: 30px;">Thresholds (ppm):<br />&bull; Good: 0-3<br />&bull; Average: 3-8<br />&bull; Poor: 8-10<br />&bull; Bad: &gt;10</p>'

NAME_SMOKE = "PM10"
ABBR_SMOKE = ""
UNITS_SMOKE = "ug/m3"
ORDER_SMOKE = 6
CONTENT_SMOKE = '<ul><li>Seek out the source of smoke and stop</li><li>Close windows and doors to avoid outside smoke</li><li>Avoid smoking indoors</li><li>Avoid smoke-producing cooking indoors</li><li>Use a HEPA filter air purifier</li><li>Further reading:&nbsp;<a href="https://homeairguides.com/air/10-ways-for-how-to-protect-yourself-from-wildfire-smoke" target="_blank">https://homeairguides.com/air/10-ways-for-how-to-protect-yourself-from-wildfire-smoke</a></li></ul><p style="padding-left: 30px;">Thresholds (ug/m3):<br />&bull; Good: 0-54<br />&bull; Average: 55-254<br />&bull; Poor: 255-424<br />&bull; Bad: &gt;424</p>'

NAME_LPG = "Liquid Petroleum Gas"
ABBR_LPG = "LPG"
UNITS_LPG = "ppm"
ORDER_LPG = 7
CONTENT_LPG = '<ul><li>Leave area of suspected leak as quickly as possible</li><li>Warn others to stay out of the area</li><li>Call local utility or just 911</li><li>Further reading:&nbsp;<a href="https://www.peoples-gas.com/all-about-gas/safety/smell/what-to-do.php" target="_blank">https://www.peoples-gas.com/all-about-gas/safety/smell/what-to-do.php</a></li></ul>'

NAME_NG = "Natural Gas"
ABBR_NG = "NG"
UNITS_NG = "ppm"
ORDER_NG = 8
CONTENT_NG = '<ul><li>Leave area of suspected leak as quickly as possible</li><li>Warn others to stay out of the area</li><li>Call local utility preferably or 911</li><li>Further reading:&nbsp;<a href="https://www.peoples-gas.com/all-about-gas/safety/smell/what-to-do.php" target="_blank">https://www.peoples-gas.com/all-about-gas/safety/smell/what-to-do.php</a></li></ul>'

NAME_eCO2 = "Equivalent Carbon Dioxide"
ABBR_eCO2 = "eCO2"
UNITS_eCO2 = "ppm"
ORDER_eCO2 = 9
CONTENT_eCO2 = '<ul><li>Wear a Mask</li><li>Avoid Crowded Places</li></ul>'

NAME_H2 = "Hydrogen"
ABBR_H2 = "H2"
UNITS_H2 = "ppm"
ORDER_H2 = 10
CONTENT_H2 = '<ul><li>Wear a Mask</li><li>Avoid Crowded Places</li></ul>'

NAME_TEMP = "Temperature"
ABBR_TEMP = "Temperature"
UNITS_TEMP = "F"
ORDER_TEMP = 1

NAME_HUMIDITY = "Humidity"
ABBR_HUMIDITY = "Humidity"
UNITS_HUMIDITY = "%"
ORDER_HUMIDITY = 1

NAME_PRESSURE = "Pressure"
ABBR_PRESSURE = "Pressure"
UNITS_PRESSURE = "inHg"
ORDER_PRESSURE = 3

NAME_ALTITUDE = "Altitude"
ABBR_ALTITUDE = "Altitude"
UNITS_ALTITUDE = "ft"
ORDER_ALTITUDE = 4


POLLUTANTS_NAMES = [NAME_PM25, NAME_TVOC, NAME_CO2, NAME_O3, NAME_CO,
                 NAME_SMOKE, NAME_LPG, NAME_NG, NAME_eCO2, NAME_H2]

POLLUTANTS_ABBR = [ABBR_PM25, ABBR_TVOC, ABBR_CO2, ABBR_O3, ABBR_CO,
                 ABBR_SMOKE, ABBR_LPG, ABBR_NG, ABBR_eCO2, ABBR_H2]

POLLUTANTS_UNITS = [UNITS_PM25, UNITS_TVOC, UNITS_CO2, UNITS_O3, UNITS_CO,
                 UNITS_SMOKE, UNITS_LPG, UNITS_NG, UNITS_eCO2, UNITS_H2]

POLLUTANTS_UNITS_EMPTY = ["", "", "", "", "",
                       "", "", "", "", ""]

POLLUTANTS_ORDER = [ORDER_PM25, ORDER_TVOC, ORDER_CO2, ORDER_O3, ORDER_CO,
                 ORDER_SMOKE, ORDER_LPG, ORDER_NG, ORDER_eCO2, ORDER_H2]

POLLUTANTS_TIPS_TITLES = [ABBR_PM25, ABBR_TVOC, ABBR_CO2, ABBR_O3, ABBR_CO,
                 NAME_SMOKE, ABBR_LPG, ABBR_NG, ABBR_eCO2, ABBR_H2]

POLLUTANTS_TIPS_CONTENTS = [CONTENT_PM25, CONTENT_TVOC, CONTENT_CO2, CONTENT_O3, CONTENT_CO,
                 CONTENT_SMOKE, CONTENT_LPG, CONTENT_NG, CONTENT_eCO2, CONTENT_H2]

WEATHER_UNITS = [UNITS_TEMP, UNITS_HUMIDITY, UNITS_PRESSURE, UNITS_ALTITUDE]
NUM_OF_POLLLUTANTS = 10
NUM_OF_WEATHER_COMP = 4


'''
@app.before_request
def before_request():
    scheme = request.headers.get('X-Forwarded-Proto')
    if scheme and scheme == 'http' and request.url.startswith('http://'):
        url = request.url.replace('http://', 'https://', 1)
        code = 301
        return redirect(url, code=code)
'''

def calculate_on_ref_Ro(sensor_raw, sensor_RL, sensor_ref_Ro, sensor_curve):
    sensor_rs = MQResistanceCalculation(sensor_raw, sensor_RL)
    sensor_rs_by_ro = (float)(sensor_rs)/sensor_ref_Ro
    sensor_ppm = MQGetPercentage(sensor_rs_by_ro, sensor_curve)

    return sensor_ppm


'''
MQResistanceCalculation
Input:   raw_adc - raw value read from adc, which represents the voltage
Output:  the calculated sensor resistance
Remarks: The sensor and the load resistor forms a voltage divider.
         Given the voltage across the load resistor and its resistance,
         the resistance of the sensor could be derived.

'''
def MQResistanceCalculation(raw_adc, rl_value):
  return ( ((float)(rl_value)*(1023-raw_adc)/raw_adc))


'''
MQGetPercentage
Input:   rs_ro_ratio - Rs divided by Ro
         pcurve      - pointer to the curve of the target gas
Output:  ppm of the target gas
Remarks: By using the slope and a point of the line.
         The x(logarithmic value of ppm) of the line could be derived
         if y(rs_ro_ratio) is provided. As it is a logarithmic coordinate,
         power of 10 is used to convert the result to non-logarithmic value.

'''

GREEN = "green"
BLUE = "blue"
ORANGE = "orange"
RED = "red"

GOOD = "GOOD"
MODERATE = "MODERATE"
POOR = "POOR"
BAD = "BAD"

'''
def get_Smoke_state_barColor(val):
    if 0 <= val < 201:
        return GOOD, GREEN
    elif 201 < val < 401:
        return MODERATE, BLUE
    elif 401 <= val < 601:
        return POOR, ORANGE
    elif val >= 600:
        return BAD, RED
'''

def get_temp_state_barColor(val):
    if 20 <= val <= 27:
        return GOOD, GREEN
    elif (16 <= val < 20) or (27 <= val <= 28):
        return MODERATE, BLUE
    elif (28 < val <= 30):
        return POOR, ORANGE
    elif val < 16 or val > 30:
        return BAD, RED

def get_humidity_state_barColor(val):
    if 30 <= val <= 50:
        return GOOD, GREEN
    elif 51 <= val <= 60:
        return MODERATE, BLUE
    elif (20 < val < 30) or (60 < val < 70):
        return POOR, ORANGE
    elif val < 20 or val > 70:
        return BAD, RED

def get_PM25_state_barColor(val):
    if 0 <= val < 13:
        return GOOD, GREEN
    elif 13 <= val < 16:
        return MODERATE, BLUE
    elif 16 <= val < 36:
        return POOR, ORANGE
    elif val >= 36:
        return BAD, RED

def get_VOC_state_barColor(val):
    if 0 <= val < 221:
        return GOOD, GREEN
    elif 221 <= val < 661:
        return MODERATE, BLUE
    elif 661 <= val < 2001:
        return POOR, ORANGE
    elif val >= 2001:
        return BAD, RED

def get_CO2_state_barColor(val):
    if 250 <= val < 1001:
        return GOOD, GREEN
    elif 1001 <= val < 2001:
        return MODERATE, BLUE
    elif 2001 <= val < 5001:
        return POOR, ORANGE
    elif val >= 5001:
        return BAD, RED

def get_O3_state_barColor(val):
    if 0 <= val < 0.06:
        return GOOD, GREEN
    elif 0.06 <= val < 0.09:
        return MODERATE, BLUE
    elif 0.09 <= val < 0.2:
        return POOR, ORANGE
    elif val >= 0.2:
        return BAD, RED

def get_CO_state_barColor(val):
    if 0 <= val < 4:
        return GOOD, GREEN
    elif 4 <= val < 9:
        return MODERATE, BLUE
    elif 9 <= val < 11:
        return POOR, ORANGE
    elif val >= 11:
        return BAD, RED

def get_Smoke_state_barColor(val):
    if 0 <= val < 55:
        return GOOD, GREEN
    elif 55 < val < 255:
        return MODERATE, BLUE
    elif 255 <= val < 425:
        return POOR, ORANGE
    elif val >= 425:
        return BAD, RED

def get_LPG_state_barColor(val):
    if 0 <= val < 21:
        return GOOD, GREEN
    elif 21 <= val < 36:
        return MODERATE, BLUE
    elif 36 <= val < 61:
        return POOR, ORANGE
    elif val >= 61:
        return BAD, RED

def get_NG_state_barColor(val):
    if 0 <= val < 21:
        return GOOD, GREEN
    elif 21 <= val < 36:
        return MODERATE, BLUE
    elif 36 <= val < 61:
        return POOR, ORANGE
    elif val >= 61:
        return BAD, RED

def get_eCO2_state_barColor(val):
    if 250 <= val < 1001:
        return GOOD, GREEN
    elif 1001 <= val < 2001:
        return MODERATE, BLUE
    elif 2001 <= val < 5001:
        return POOR, ORANGE
    elif val >= 5001:
        return BAD, RED

def get_H2_state_barColor(val):
    if 0 <= val < 4:
        return GOOD, GREEN
    elif 4 <= val < 9:
        return MODERATE, BLUE
    elif 9 <= val < 11:
        return POOR, ORANGE
    elif val >= 11:
        return BAD, RED

humidity_max = 70
temp_max = 30
PM25_max = 35
tVOC_max = 2000
O3_max = 0.2
CO2_max = 5000
CO_max = 50
Smoke_max = 610
NG_max = 100
LPG_max = 100

'''
Smoke_max = 5000
NG_max = 5000
LPG_max = 5000
'''

# returns in multiples of 10. 0-100, including both
def get_barValue(value, maxValue):
    #return Math.min(Math.round(value / maxValue * 10) * 10, 100)
    value =  min(math.floor(float(value) / maxValue * 10) * 10, 100)
    print (value)
    if value < 1:
        value = 5

    return value

def MQGetPercentage(rs_ro_ratio, pcurve):
    # Python program explaining
    # log() function
    val1 = np.log(rs_ro_ratio)
    numerator = val1 - pcurve[1]
    fraction = float(numerator)/pcurve[2]
    exponent = fraction + pcurve[0]
    base = 10

    result = base ** exponent
    return result


def parse_date(date_str):
    yyyy_mm_dd = date_str.split('-')
    yyyy = int(yyyy_mm_dd[0])
    mm = int(yyyy_mm_dd[1])
    dd = int(yyyy_mm_dd[2])
    date_obj = date(year=yyyy,month=mm,day=dd)

    return date_obj


def create_datetime_obj(datestr, delimiter=" "):
    # An example input string: '2019-12-23 10:23:14.472074'
    # Example 2: 2019-12-21T05:01:49.542965+00:00
    ds = datestr.split(delimiter)

    # creates YYYY MM DD tokens
    # Example: ['2019', '12', '23']
    date_tokens = ds[0].split("-")
    yyyy = int(date_tokens[0])
    mm = int(date_tokens[1])
    dd = int(date_tokens[2])

    time_str_tokens = ds[1].split("+")

    # Example: ['10', '23', '14.472074']
    time_tokens = time_str_tokens[0].split(":")
    hr = int(time_tokens[0])
    mn = int(time_tokens[1])

    # Example: ['14', '472074']
    time_sec_tokens = time_tokens[2].split(".")
    sec = int(time_sec_tokens[0])
    ms = int(time_sec_tokens[1])

    #print ("{} {} {} {} {} {} {}".format(yyyy, mm, dd, hr, mn, sec, ms))
    # datetime(year, month, day, hour, minute, second, microsecond)
    datetime_obj = datetime(yyyy, mm, dd, hr, mn, sec, ms)

    return datetime_obj


@app.route('/api/air/zipcode/<zipcode>/atmosome/timeseries/<filename>', methods=['GET'])
def data_by_graph_file(zipcode, filename):
    print ("------- I am in data_by_graph_file -------")
    try:
        return send_from_directory(app.config["CLIENT_GRAPHS"],
                                   filename=filename,
                                   as_attachment=True)
    except FileNotFoundError:
        abort(404)

@app.route('/api/air/zipcode/<zipcode>/timeseries/graphs/smoke/<filename>', methods=['GET'])
def data_by_smoke_graph_file(zipcode, filename):
    try:
        return send_from_directory(app.config["CLIENT_GRAPHS"],
                                   filename=filename,
                                   as_attachment=True)
    except FileNotFoundError:
        abort(404)


@app.route('/api/air/zipcode/<zipcode>/timeseries/graphs/ng/<filename>', methods=['GET'])
def data_by_ng_graph_file(zipcode, filename):
    try:
        return send_from_directory(app.config["CLIENT_GRAPHS"],
                                   filename=filename,
                                   as_attachment=True)
    except FileNotFoundError:
        abort(404)


@app.route('/api/air/zipcode/<zipcode>/timeseries/csv', methods=['GET'])
def csv_timeseries(zipcode, num_of_days=TIMESERIES_QUARTER):
    # Read configs_dir/thresholds.json
    ts_config = "{}/{}".format(app.config["CLIENT_CONFIGS"], TS_THRESHOLDS_JSON)
    with open(ts_config, "r") as thresholds_file:
        # Converting JSON encoded data into Python dictionary
        thresholds_data = json.load(thresholds_file)
        thresholds = thresholds_data["thresholds"]

    cur_date = datetime.now()
    cur_time = time.time()
    # GAYATRI
    past_time = cur_date - timedelta(days=num_of_days)

    t1 = time.time()

    airdata = Air.query.with_entities(
            Air.timestamp,
            Air.city,
            Air.state,
            Air.country,
            Air.zipcode,
            Air.place,
            Air.details,
            Air.misc,
            Air.temp,
            Air.humidity,
            Air.pressure,
            Air.altitude,
            Air.dustDensity,
            Air.tVOC,
            Air.co2_ppm,
            Air.mq131_o3_ppm,
            Air.mq7_co_ppm,
            Air.mq2_smoke_ppm,
            Air.eCO2,
            Air.mq6_lpg_ppm,
            Air.mq4_ng_ppm,
            Air.mq7_h2_ppm
            ).filter(Air.zipcode == zipcode, Air.timestamp >= past_time).all()

    if not airdata:
        return jsonify({}), 200

    df = pd.DataFrame(airdata,columns=['timestamp','city', 'state', 'country', 'zipcode', 'place', 'details', 'misc', 'temp', 'humidity', 'pressure', 'altitude', 'pm2_5','tVOC', 'co2', 'o3', 'co', 'pm10', 'eCO2', 'lpg', 'ng', 'h2'])
    t2 = time.time()

        #csv_columns = ["air_id", "timestamp", "city", "state", "country", "zipcode", "place", "details", "misc", "tVOC", "eCO2", "temp", "pressure", "altitude", "humidity", "mq2_smoke_ppm", "mq4_ng_ppm", "mq6_lpg_ppm", "mq7_co_ppm", "mq131_o3_ppm", "co2_ppm", "dustDensity"]

        #data_pm25.loc[data_pm25['PM2.5'] > 40, 'PM2.5'] = 40

    if zipcode == '94720':
        df.loc[df['altitude'] < 150, 'altitude'] = 177.0
        df.loc[df['altitude'] > 210, 'altitude'] = 177.0
    elif zipcode == '95014':
        df.loc[df['altitude'] < 180, 'altitude'] = 236.0
        df.loc[df['altitude'] > 250, 'altitude'] = 236.0
    elif zipcode == '95064':
        df.loc[df['altitude'] < 650, 'altitude'] = 763.0
        df.loc[df['altitude'] > 850, 'altitude'] = 763.0
    elif zipcode == '96150':
        df.loc[df['altitude'] < 5500, 'altitude'] = 6263.0
        df.loc[df['altitude'] > 6350, 'altitude'] = 6263.0
    elif zipcode == '94305':
        df.loc[df['altitude'] < 135, 'altitude'] = 141.0
        df.loc[df['altitude'] > 155, 'altitude'] = 141.0

    df['co'] = df['co']/10
    df['pm10'] = df['pm10']/10

    print ("%%%%%%%%%%%%%% NEW DF %%%%%%%%%%%")
    fname = datetime.utcnow()
    csv_fname = "{}.csv".format(fname)
    csv_fname = csv_fname.replace(" ", "_")
    csv_file_with_dir_name = "{}/{}".format(app.config["CLIENT_CSVS"], csv_fname)
    print ("*********************** GB *************")
    print (csv_fname)
    print (csv_file_with_dir_name)
    csv_url = "{}/downloads/{}".format(request.url, csv_fname)
    print ("*********************** GB *************")
    df.to_csv (csv_file_with_dir_name, index = False, header=True)

    print (t2-t1)

    print ("####### URLS request.url, csv_filename, csv_url ########")
    print (request.url)
    print (csv_fname)
    print (csv_url)
    print ("%%%%%%%%%%%%%% END DF %%%%%%%%%%%")


    message = ("Please download the file in csv format by pasting this link in the browser: "
               "{}"
               ).format(csv_url)
    return jsonify({'air_data_csv_file': message}), 200


    try:
        return send_from_directory(app.config["CLIENT_CSVS"],
                                   filename=csv_fname,
                                   as_attachment=True)
    except FileNotFoundError:
        abort(404)


@app.route('/api/air/zipcode/<zipcode>/timeseries/csv/days/<num_of_days>', methods=['GET'])
def csv_timeseries_num_days(zipcode, num_of_days):
    days = int(num_of_days)
    return csv_timeseries(zipcode, days)


def plot_timeseries(data, name, unit, zipcode, current_time, lines_data=None):
    # plot data
    print ("^%^%^%^%^%^%^%^%^%^%")
    print ("ENTER plot_timeseries")
    print ("^%^%^%^%^%^%^%^%^%^%")

    fig, ax = plt.subplots(figsize=(25,7))

    num_of_data_points = data[data.columns[0]].count()
    print ("num_of_data_points")
    print (num_of_data_points)

    data.plot(ax=ax)
    ax.grid(True, which='both')

    # set margin, labels and font size
    y_label = "{} {}".format(name, unit)
    plt.margins(x=0)
    plt.xlabel('Timestamps', size=24)
    plt.ylabel(y_label, size=24)
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)

    # set ticks every Mon and Fri
    #loc = mdates.WeekdayLocator(byweekday=(MO,FR))

    if num_of_data_points < 1000:
        loc = mdates.WeekdayLocator(byweekday=(MO,FR))
    elif num_of_data_points < 2000:
        loc = mdates.WeekdayLocator(byweekday=(MO))
    elif num_of_data_points < 3000:
        loc = mdates.WeekdayLocator(byweekday=MO, interval=2)
    else:
        loc = mdates.WeekdayLocator(byweekday=MO, interval=3)
    print ("LOC LOC LOC")
    print (loc)
    print ("LOC LOC LOC")
    ax.xaxis.set_major_locator(loc)

    # plot the threshold value lines
    for line_data in lines_data:
        plt.axhline(line_data["value"], color=line_data["color"])

    # save plot
    file_name = "{}_{}_{}.png".format(name, zipcode, current_time)
    file_name_path = "{}/{}".format(app.config["CLIENT_GRAPHS"], file_name)
    plt.savefig(file_name_path)

    # graph URL
    graph_url = "{}/{}".format(request.url, file_name)
    print ("^%^%^%^%^%^%^%^%^%^%")
    print ("Exiting plot_timeseries")
    print (graph_url)
    print ("^%^%^%^%^%^%^%^%^%^%")
    return graph_url


@app.route('/api/air/zipcode/<zipcode>/timeseries/graphs/smoke', methods=['GET'])
def timeseries_graph_smoke(zipcode, num_of_days=TIMESERIES_QUARTER):
    # Read configs_dir/thresholds.json
    ts_config = "{}/{}".format(app.config["CLIENT_CONFIGS"], TS_THRESHOLDS_JSON)
    with open(ts_config, "r") as thresholds_file:
        # Converting JSON encoded data into Python dictionary
        thresholds_data = json.load(thresholds_file)
        thresholds = thresholds_data["thresholds"]

    cur_date = datetime.now()
    cur_time = time.time()
    # GAYATRI
    past_time = cur_date - timedelta(days=num_of_days)
    #past_time = cur_date - timedelta(days=num_of_days)

    t1 = time.time()

    airdata = Air.query.with_entities(
            Air.timestamp,
            Air.mq2_smoke_ppm
            ).filter(Air.zipcode == zipcode, Air.timestamp >= past_time).all()

    t2 = time.time()
    print ("%% AIR DATA FOR TIMESERIES  HERE ENTER %%")
    print ("airdata: {}".format(airdata))
    print ("%% AIR DATA FOR TIMESERIES EXIT if NONE %%")

    if not airdata:
        return {}

    print ("%%%%%%%%%%%%%% TS %%%%%%%%%%%")
    #print (t2-t1)
    #print ("airData[0]: ")
    #print (airdata[0])
    #print (airdata[1])
    #print (airdata[2])
    #print (airdata[3])
    print ("%%%%%%%%%%%%%% END TS %%%%%%%%%%%")

    t1 = time.time()
    air_zip = zip(*airdata)

    tmp_air_list = list(air_zip)
    air_ts = tmp_air_list[:]




    print (type(air_ts))
    print (air_ts)
    t2 = time.time()
    print ("%%%%%%%%%%%%%% TRANSPOSE %%%%%%%%%%%")
    print (t2-t1)
    print (len(air_ts))
    print ("%%%%%%%%%%%%%% END TRANSPOSE %%%%%%%%%%%")

    t1 = time.time()

    l_time = air_ts[0]

    # print ("------- pm25 ------------")
    l_pm10 = air_ts[1]
    d_pm10 = {"timestamp": l_time, "PM10": l_pm10}
    data_pm10 = pd.DataFrame(d_pm10)
    data_pm10["timestamp"] = pd.to_datetime(data_pm10["timestamp"])
    data_pm10.set_index('timestamp',inplace=True)
    thresholds_pm10 = thresholds["pm10"]["lines"]
    graph_pm10 = plot_timeseries(data_pm10, ABBR_SMOKE, UNITS_SMOKE, zipcode,
                                 cur_time, thresholds_pm10)


    t2 = time.time()
    print ("^^^^^^^^^^ DATA READINESS ^^^^^^^^^")
    print (t2-t1)
    print ("^^^^^^^^^^ END DATA READINESS ^^^^^^^^^")


    data = {
            "ts_pm10": graph_pm10
            }

    return data

@app.route('/api/air/zipcode/<zipcode>/timeseries/graphs/ng', methods=['GET'])
def timeseries_graph_ng(zipcode, num_of_days=TIMESERIES_QUARTER):
    # Read configs_dir/thresholds.json
    ts_config = "{}/{}".format(app.config["CLIENT_CONFIGS"], TS_THRESHOLDS_JSON)
    with open(ts_config, "r") as thresholds_file:
        # Converting JSON encoded data into Python dictionary
        thresholds_data = json.load(thresholds_file)
        thresholds = thresholds_data["thresholds"]

    cur_date = datetime.now()
    cur_time = time.time()
    # GAYATRI
    past_time = cur_date - timedelta(days=num_of_days)
    #past_time = cur_date - timedelta(days=num_of_days)

    t1 = time.time()

    airdata = Air.query.with_entities(
            Air.timestamp,
            Air.mq4_ng_ppm
            ).filter(Air.zipcode == zipcode, Air.timestamp >= past_time).all()

    t2 = time.time()
    print ("%% AIR DATA FOR TIMESERIES  HERE ENTER %%")
    print ("airdata: {}".format(airdata))
    print ("%% AIR DATA FOR TIMESERIES EXIT if NONE %%")

    if not airdata:
        return {}

    print ("%%%%%%%%%%%%%% TS %%%%%%%%%%%")
    #print (t2-t1)
    #print ("airData[0]: ")
    #print (airdata[0])
    #print (airdata[1])
    #print (airdata[2])
    #print (airdata[3])
    print ("%%%%%%%%%%%%%% END TS %%%%%%%%%%%")

    t1 = time.time()
    air_zip = zip(*airdata)

    tmp_air_list = list(air_zip)
    air_ts = tmp_air_list[:]




    print (type(air_ts))
    print (air_ts)
    t2 = time.time()
    print ("%%%%%%%%%%%%%% TRANSPOSE %%%%%%%%%%%")
    print (t2-t1)
    print (len(air_ts))
    print ("%%%%%%%%%%%%%% END TRANSPOSE %%%%%%%%%%%")

    t1 = time.time()

    l_time = air_ts[0]

    # print ("------- pm25 ------------")
    l_ng = air_ts[1]
    d_ng = {"timestamp": l_time, "NG": l_ng}
    data_ng = pd.DataFrame(d_ng)
    data_ng["timestamp"] = pd.to_datetime(data_ng["timestamp"])
    data_ng.set_index('timestamp',inplace=True)
    thresholds_ng = thresholds["ng"]["lines"]
    graph_ng = plot_timeseries(data_ng, ABBR_NG, UNITS_NG, zipcode,
                                 cur_time, thresholds_ng)


    t2 = time.time()
    print ("^^^^^^^^^^ DATA READINESS ^^^^^^^^^")
    print (t2-t1)
    print ("^^^^^^^^^^ END DATA READINESS ^^^^^^^^^")


    data = {
            "ts_ng": graph_ng
            }

    return data


@app.route('/api/air/zipcode/<zipcode>/timeseries/graphs', methods=['GET'])
def timeseries_graphs(zipcode, num_of_days=TIMESERIES_QUARTER):
    # Read configs_dir/thresholds.json
    ts_config = "{}/{}".format(app.config["CLIENT_CONFIGS"], TS_THRESHOLDS_JSON)
    with open(ts_config, "r") as thresholds_file:
        # Converting JSON encoded data into Python dictionary
        thresholds_data = json.load(thresholds_file)
        thresholds = thresholds_data["thresholds"]

    cur_date = datetime.now()
    cur_time = time.time()
    # GAYATRI
    past_time = cur_date - timedelta(days=num_of_days)
    #past_time = cur_date - timedelta(days=num_of_days)

    t1 = time.time()

    airdata = Air.query.with_entities(
            Air.timestamp,
            Air.dustDensity,
            Air.tVOC,
            Air.co2_ppm,
            Air.mq131_o3_ppm,
            Air.temp,
            Air.humidity
            ).filter(Air.zipcode == zipcode, Air.timestamp >= past_time).all()

    t2 = time.time()
    print ("%% AIR DATA FOR TIMESERIES  HERE ENTER %%")
    print ("airdata: {}".format(airdata))
    print ("%% AIR DATA FOR TIMESERIES EXIT if NONE %%")

    if not airdata:
        return {}

    print ("%%%%%%%%%%%%%% TS %%%%%%%%%%%")
    #print (t2-t1)
    #print ("airData[0]: ")
    #print (airdata[0])
    #print (airdata[1])
    #print (airdata[2])
    #print (airdata[3])
    print ("%%%%%%%%%%%%%% END TS %%%%%%%%%%%")

    t1 = time.time()
    air_zip = zip(*airdata)
    
    tmp_air_list = list(air_zip)
    air_ts = tmp_air_list[:]




    print (type(air_ts))
    print (air_ts)
    t2 = time.time()
    print ("%%%%%%%%%%%%%% TRANSPOSE %%%%%%%%%%%")
    print (t2-t1)
    print (len(air_ts))
    print ("%%%%%%%%%%%%%% END TRANSPOSE %%%%%%%%%%%")

    t1 = time.time()

    l_time = air_ts[0]

    # print ("------- pm25 ------------")
    l_pm25 = air_ts[1]
    d_pm25 = {"timestamp": l_time, "PM2.5": l_pm25}
    data_pm25 = pd.DataFrame(d_pm25)
    data_pm25.loc[data_pm25['PM2.5'] > 40, 'PM2.5'] = 40
    data_pm25["timestamp"] = pd.to_datetime(data_pm25["timestamp"])
    data_pm25.set_index('timestamp',inplace=True)
    thresholds_pm25 = thresholds["pm25"]["lines"]
    graph_pm25 = plot_timeseries(data_pm25, ABBR_PM25, UNITS_PM25, zipcode,
                                 cur_time, thresholds_pm25)

    # print ("------- tVOC ------------")
    l_tVOC = air_ts[2]
    d_tVOC = {"timestamp": l_time, "VOC": l_tVOC}
    data_tVOC = pd.DataFrame(d_tVOC)
    data_tVOC.loc[data_tVOC['VOC'] > 2200, 'VOC'] = 2200
    data_tVOC["timestamp"] = pd.to_datetime(data_tVOC["timestamp"])
    data_tVOC.set_index('timestamp',inplace=True)
    thresholds_tVOC = thresholds["tVOC"]["lines"]
    graph_tVOC = plot_timeseries(data_tVOC, ABBR_TVOC, UNITS_TVOC, zipcode,
                                 cur_time, thresholds_tVOC)

    # print ("------- co2 ------------")
    l_co2 = air_ts[3]
    d_co2 = {"timestamp": l_time, "CO2": l_co2}
    data_co2 = pd.DataFrame(d_co2)
    print ("DEBUG THIS MORNING")
    #df.loc[df['c1'] == 'Value', 'c2'] = 10
    data_co2.loc[data_co2['CO2'] > 5500, 'CO2'] = 5500
    print ("DEBUG THIS MORNING")
    data_co2["timestamp"] = pd.to_datetime(data_co2["timestamp"])
    data_co2.set_index('timestamp',inplace=True)
    thresholds_co2 = thresholds["co2"]["lines"]
    graph_co2 = plot_timeseries(data_co2, ABBR_CO2, UNITS_CO2, zipcode,
                                cur_time, thresholds_co2)

    # print ("------- o3 ------------")
    l_o3 = air_ts[4]
    d_o3 = {"timestamp": l_time, "O3": l_o3}
    data_o3 = pd.DataFrame(d_o3)
    data_o3["timestamp"] = pd.to_datetime(data_o3["timestamp"])
    data_o3.set_index('timestamp',inplace=True)
    thresholds_o3 = thresholds["o3"]["lines"]
    graph_o3 = plot_timeseries(data_o3, ABBR_O3, UNITS_O3, zipcode, cur_time,
                               thresholds_o3)

    # print ("------- temp ------------")
    l_temp = air_ts[5]
    d_temp = {"timestamp": l_time, "Temperature": l_temp}
    data_temp = pd.DataFrame(d_temp)
    data_temp["timestamp"] = pd.to_datetime(data_temp["timestamp"])
    data_temp.set_index('timestamp',inplace=True)
    thresholds_temp = thresholds["temp"]["lines"]
    graph_temp = plot_timeseries(data_temp, ABBR_TEMP, UNITS_TEMP, zipcode,
                                 cur_time, thresholds_temp)

    # print ("------- hum ------------")
    l_hum = air_ts[6]
    d_hum = {"timestamp": l_time, "Humidity": l_hum}
    data_hum = pd.DataFrame(d_hum)
    data_hum["timestamp"] = pd.to_datetime(data_hum["timestamp"])
    data_hum.set_index('timestamp',inplace=True)
    thresholds_hum = thresholds["humidity"]["lines"]
    graph_hum = plot_timeseries(data_hum, ABBR_HUMIDITY, UNITS_HUMIDITY,
                                zipcode, cur_time, thresholds_hum)

    t2 = time.time()
    print ("^^^^^^^^^^ DATA READINESS ^^^^^^^^^")
    print (t2-t1)
    print ("^^^^^^^^^^ END DATA READINESS ^^^^^^^^^")


    data = {
            "ts_pm25": graph_pm25,
            "ts_tVOC": graph_tVOC,
            "ts_co2": graph_co2,
            "ts_o3": graph_o3,
            "ts_temp": graph_temp,
            "ts_humidity": graph_hum
            }

    return data



def timeseries_data(zipcode):
    graphs = timeseries_graphs(zipcode)

    if not graphs:
        ts_data = {
            "timeSeriesData": []
        }
        return ts_data

    data_pm25 = {
        "name": "PM2.5",
        "graphImageUrl": graphs["ts_pm25"],
        "order": 1
    }

    data_tVOC = {
        "name": "tVOC",
        "graphImageUrl": graphs["ts_tVOC"],
        "order": 2
    }

    data_co2 = {
        "name": "CO2",
        "graphImageUrl": graphs["ts_co2"],
        "order": 3
    }

    data_o3 = {
        "name": "O3",
        "graphImageUrl": graphs["ts_o3"],
        "order": 4
    }

    data_temp = {
        "name": "Temperature",
        "graphImageUrl": graphs["ts_temp"],
        "order": 5
    }

    data_hum = {
        "name": "Humidity",
        "graphImageUrl": graphs["ts_humidity"],
        "order": 6
    }

    ts_data = {
        "timeSeriesData": [data_pm25, data_tVOC, data_co2, data_o3,
                           data_temp, data_hum]
    }

    #print (ts_data)
    return ts_data


def ORIGINAL_SUMMARY_cumulative_data(zipcode, num_of_days):
    past_time = datetime.now() - timedelta(days=num_of_days)

    #t1 = time.time()
    airdata = Air.query.with_entities(
            func.sum(Air.dustDensity).label('avg_pm25'),
            func.sum(Air.tVOC).label('avg_tVOC'),
            func.sum(Air.co2_ppm).label('avg_co2'),
            func.sum(Air.mq131_o3_ppm).label('avg_o3')
            ).filter(Air.zipcode == zipcode, Air.timestamp >= past_time).all()

    #t2 = time.time()
    if not airdata:
        return {}

    air_aggrs = airdata[0]

    #t3 = time.time()
    data = {
            "total_pm25": air_aggrs[0],
            "total_tVOC": air_aggrs[1],
            "total_co2": air_aggrs[2],
            "total_o3": air_aggrs[3]
            }
    #print (data)
    return data

def cumulative_data(zipcode, num_of_hours):
    past_time = datetime.now() - timedelta(hours=num_of_hours)

    #t1 = time.time()
    airdata = Air.query.with_entities(
            func.avg(Air.dustDensity).label('avg_pm25'),
            func.avg(Air.tVOC).label('avg_tVOC'),
            func.avg(Air.co2_ppm).label('avg_co2'),
            func.avg(Air.mq131_o3_ppm).label('avg_o3')
            ).filter(Air.zipcode == zipcode, Air.timestamp >= past_time).all()

    #t2 = time.time()
    if not airdata:
        data = {
            "avg_pm25": "N/A",
            "avg_tVOC": "N/A",
            "avg_co2": "N/A",
            "avg_o3": "N/A"
            }
        return data

    air_aggrs = airdata[0]

    if not air_aggrs:
        data = {
            "avg_pm25": "N/A",
            "avg_tVOC": "N/A",
            "avg_co2": "N/A",
            "avg_o3": "N/A"
            }
        return data
    else:
        if air_aggrs[0]:
            val_pm25 = round(air_aggrs[0], 2)
        else:
            val_pm25 = "N/A"

        if air_aggrs[1]:
            val_tVOC = round(air_aggrs[1], 2)
        else:
            val_tVOC = "N/A"

        if air_aggrs[2]:
            val_co2 = round(air_aggrs[2], 2)
        else:
            val_co2 = "N/A"

        if air_aggrs[3]:
            val_o3 = round(air_aggrs[3], 2)
        else:
            val_o3 = "N/A"

    #t3 = time.time()
    data = {
            "avg_pm25": val_pm25,
            "avg_tVOC": val_tVOC,
            "avg_co2": val_co2,
            "avg_o3": val_o3
            }
    #print (data)
    return data


def cumulative_exposure_data(zipcode):
    #past_8_hours = cumulative_data(zipcode, 22)
    past_8_hours = cumulative_data(zipcode, 8)
    past_24_hours = cumulative_data(zipcode, 24)
    past_week = cumulative_data(zipcode, 168)

    data_pm25 = {
        "name": ABBR_PM25,
        "unit": UNITS_PM25,
        "order": 1,
        "stats": [
            {
                "title": "8 Hours",
                "order": 1,
                "stats": past_8_hours["avg_pm25"]
            },
            {
                "title": "24 Hours",
                "order": 2,
                "stats": past_24_hours["avg_pm25"]
            },
            {
                "title": "1 week",
                "order": 3,
                "stats": past_week["avg_pm25"]
            }
        ]
    }

    data_tVOC = {
        "name": ABBR_TVOC,
        "unit": UNITS_TVOC,
        "order": 2,
        "stats": [
            {   
                "title": "8 Hours",
                "order": 1,
                "stats": past_8_hours["avg_tVOC"]
            },
            {   
                "title": "24 Hours",
                "order": 2,
                "stats": past_24_hours["avg_tVOC"]
            },
            {   
                "title": "1 week",
                "order": 3,
                "stats": past_week["avg_tVOC"]
            }
        ]
    }

    data_co2 = {
        "name": ABBR_CO2,
        "unit": UNITS_CO2,
        "order": 3,
        "stats": [
            {
                "title": "8 Hours",
                "order": 1,
                "stats": past_8_hours["avg_co2"]
            },
            {
                "title": "24 Hours",
                "order": 2,
                "stats": past_24_hours["avg_co2"]
            },
            {
                "title": "1 week",
                "order": 3,
                "stats": past_week["avg_co2"]
            }
        ]
    }

    data_o3 = {
        "name": ABBR_O3,
        "unit": UNITS_O3,
        "order": 4,
        "stats": [
            {
                "title": "8 Hours",
                "order": 1,
                "stats": past_8_hours["avg_o3"]
            },
            {
                "title": "24 Hours",
                "order": 2,
                "stats": past_24_hours["avg_o3"]
            },
            {
                "title": "1 week",
                "order": 3,
                "stats": past_week["avg_o3"]
            }
        ]
    }

    average_exposure = {
        "averageExposure": [data_pm25, data_tVOC, data_co2, data_o3]
    }

    return average_exposure


def calculate_ugm3(weight, ppb):
    return (ppb * (weight/22.41))


def hourly_data(zipcode, num_of_hours=ONE_HOUR):
    pollutants_vals = ["N/A"] * NUM_OF_POLLLUTANTS
    pollutants_units = [""] * NUM_OF_POLLLUTANTS
    bar_vals = [0] * NUM_OF_POLLLUTANTS
    bar_colors = ["GREEN"] * NUM_OF_POLLLUTANTS
    pollutants_states = ["N/A"] * NUM_OF_POLLLUTANTS
    weather_vals = ["N/A"]*4
    weather_units = [""]*4
    aqi_val = 0

    POLLUTANTS_DATA_AVAILABLE = True
    WEATHER_DATA_AVAILABLE = True

    past_time = datetime.now() - timedelta(hours=num_of_hours)

    airdata = Air.query.with_entities(
            func.avg(Air.dustDensity).label('avg_pm25'),
            func.avg(Air.tVOC).label('avg_tVOC'),
            func.avg(Air.co2_ppm).label('avg_co2'),
            func.avg(Air.mq131_o3_ppm).label('avg_o3'),
            func.avg(Air.mq7_co_ppm).label('avg_co'),
            func.avg(Air.mq2_smoke_ppm).label('avg_smoke'),
            func.avg(Air.mq6_lpg_ppm).label('avg_lpg'),
            func.avg(Air.mq4_ng_ppm).label('avg_ng'),
            func.avg(Air.eCO2).label('avg_eCO2'),
            func.avg(Air.mq7_h2_ppm).label('avg_h2'),
            func.avg(Air.temp).label('avg_temp'),
            func.avg(Air.humidity).label('avg_humidity'),
            func.avg(Air.pressure).label('avg_pressure'),
            func.avg(Air.altitude).label('avg_altitude')
            ).filter(Air.zipcode == zipcode, Air.timestamp >= past_time).all()

    print (airdata)
    print ("^^^^^^^^^^^^^^^^^^")

    air_avgs = airdata[0]



    total_nones = air_avgs.count(None)
    if total_nones == 14:
        POLLUTANTS_DATA_AVAILABLE = False
        WEATHER_DATA_AVAILABLE = False
    else:
        pollut_nones = air_avgs[:10].count(None)
        weather_nones = air_avgs[10:].count(None)

        if pollut_nones == 10:
            POLLUTANTS_DATA_AVAILABLE = False
        if weather_nones == 4:
            WEATHER_DATA_AVAILABLE = False

    # POLLUTANT ORDER in the arrays
    # PM25, TVOC, CO2, O3, CO, SMOKE, LPG, NG, eCO2, H2, TEMP, HUMIDITY, PRESSURE, ALTITUDE]
    '''
    [Tue Sep 29 17:13:48.301222 2020] [wsgi:error] [pid 30589:tid 139834142594816] [remote 69.110.136.169:50574] %%%%%%%% BEGIN AVERAGES 
    [Tue Sep 29 17:13:48.301238 2020] PM2.5      14.3315846994536
    [Tue Sep 29 17:13:48.301249 2020] TVOC       29.6338797814208
    [Tue Sep 29 17:13:48.301260 2020] CO2        1565.87978142077
    [Tue Sep 29 17:13:48.301271 2020] O3         0.0278196721311475
    [Tue Sep 29 17:13:48.301284 2020] CO         0.632240437158469
    [Tue Sep 29 17:13:48.301295 2020] SMOKE      364.229508196721
    [Tue Sep 29 17:13:48.301307 2020] LPG        1.28360655737705
    [Tue Sep 29 17:13:48.301319 2020] NG         1.56224043715847
    [Tue Sep 29 17:13:48.301331 2020] eCO2       597.622950819672
    [Tue Sep 29 17:13:48.301341 2020] H2         0.0
    [Tue Sep 29 17:13:48.301353 2020] TEMP       19.2928961748634
    [Tue Sep 29 17:13:48.301364 2020] HUMIDITY   58.0546448087432
    [Tue Sep 29 17:13:48.301376 2020] PRESSURE   100455.65852459
    [Tue Sep 29 17:13:48.301387 2020] ALTITUDE   72.6219672131148
    '''

    if WEATHER_DATA_AVAILABLE:
        # altitude adjustment
        '''
        val = air_avgs[13]
        if zipcode == '94720':
            if  val < 150:
                val = 177.0
        elif zipcode == '95014':
            if  val < 180:
                val = 236.0
        elif zipcode == '96150':
            if  val < 5500:
                val = 6263.0
        '''

        val = air_avgs[13]
        if zipcode == '94720':
            if  val < 150:
                val = 177.0
            elif  val > 210:
                val = 177.0
        elif zipcode == '95014':
            if  val < 180:
                val = 236.0
            elif  val > 250:
                val = 236.0
        elif zipcode == '95064':
            if  val < 650:
                val = 763.0
            elif  val > 850:
                val = 763.0
        elif zipcode == '96150':
            if  val < 5500:
                val = 6263.0
            elif  val > 6350:
                val = 6263.0
        elif zipcode == '94305':
            if  val < 135:
                val = 141.0
            elif  val > 155:
                val = 141.0

        '''
        if air_avgs[13] < 30:
            val = air_avgs[13] * 5
        else:
            val = air_avgs[13]
            if val < 80:
                val = 115
        '''
        weather_vals = [air_avgs[10], air_avgs[11], air_avgs[12], val]
        #weather_vals = [air_avgs[10], air_avgs[11], air_avgs[12], air_avgs[13]]
        weather_units = WEATHER_UNITS


    if POLLUTANTS_DATA_AVAILABLE:
        lpgval = air_avgs[6]
        while lpgval > 10:
            lpgval = lpgval/10

        ng_val = air_avgs[7]

        co_val = air_avgs[4]/10
        smoke_val = air_avgs[5]/10
        #while ng_val > 10:
        #    ng_val = ng_val/10


        pollutants_vals = [air_avgs[0], air_avgs[1], air_avgs[2], air_avgs[3],
                               co_val, smoke_val, lpgval, ng_val,
                            air_avgs[8], air_avgs[9]]

        ''' ORG
        pollutants_vals = [air_avgs[0], air_avgs[1], air_avgs[2], air_avgs[3],
                            air_avgs[4], air_avgs[5], lpgval, ng_val,
                            air_avgs[8], air_avgs[9]]
        '''

        '''
        pollutants_vals = [air_avgs[0], air_avgs[1], air_avgs[2], air_avgs[3],
                            air_avgs[4], air_avgs[5], air_avgs[6], air_avgs[7],
                            air_avgs[8], air_avgs[9]]
        '''
        '''
        PM2.5 - 1.248920438
        PM10 - 0.740816327
        SO2 - 0.400181718
        O3 - 0.429166667
        CO - 5.37414966
        NO2 - 0.252687954
        '''

        print (air_avgs)
        print ("------- vals --------")
        # PM25, tVOC, CO2, O3, CO
        # (21.4408333333333, 
        # 7.92857142857143, 
        # 459.70630952381, 
        # 0.0611547619047619, 
        # 8.01428571428571, 
        # 4444.63095238095, 0.0, 5.9522619047619, 455.154761904762, 0.0, 84.4035714285714, 44.0238095238095, 29.7013095238095, 203.990238095238)


        # [(19.7606666666667, 240.083333333333, 1528.04866666667, 0.03175, 4.23333333333333, 0.0, 0.0, 2.7565, 1559.23333333333, 0.0, 77.8516666666667, 38.2166666666667, 29.682, 220.803833333333)]

        #aqi_val = air_avgs[0]*1.248920438 + air_avgs[1]*0.740816327 + air_avgs[2]*0.400181718 + air_avgs[3]*0.429166667 + air_avgs[4]*5.37414966
        #aqi_val = air_avgs[0]*1.248920438 + air_avgs[1]*0.740816327 + air_avgs[3]*0.429166667 + air_avgs[4]*5.37414966



        '''
        Nitrogen dioxide 1 ppb = 1.91 ug/m3
        Sulphur dioxide 1 ppb = 2.66 ug/m3
        Ozone 1 ppb = 2.0 ug/m3
        Carbon monoxide 1 ppb = 1.16 ug/m3
        Benzene 1 ppb = 3.24 ug/m3

        SO2 - 0.400181718
        NO2 - 0.252687954
        PM10 - 0.740816327
        O3 - 0.429166667
        PM2.5 - 1.248920438
        CO - 0.00537414966
        '''
        '''

        #0.0409 x concentration (ppm) x molecular weigh
        # https://www.teesing.com/en/page/library/tools/ppm-mg3-converter
        0.0409 * <ppm> * <mol_weight>
        # PM25, tVOC, CO2, O3, CO, Smoke, LPG, NG, eCO2, H2
        tvoc_ug_m3 = 0.0409 * 78.9516 * air_avgs[1]
        co2_ug_m3 = 0.0409 * 44.01 * air_avgs[2]


        caluclate_ugm3
        if (counter == NO2)
           # no2 values produced are already in ppb
           ugm3_no2 = 	caluclate_ugm3(46.01, no2_counter_value)
        elif (counter == SO2)
           # so2 values produced are already in ppb
           ugm3_so2 = 	caluclate_ugm3(64.06, so2_counter_value)
                elif (counter == O3)   
           # O3 values produced are already in ppm in atomosme
           ugm3_o3 = 	caluclate_ugm3(48.00, O3_counter_value/1000)
        elif (counter == CO)   
           # CO values produced are already in ppm
           ugm3_co = caluclate_ugm3(28.01, co_counter_value/1000)  
       '''

        #air_avgs[1] = 1549.83
        #air_avgs[3] = 0.12

        # Replacing no2 with co2
        # Replacing so2 with tVOC
        ugm3_pm25 = air_avgs[0]
        #ugm3_tvoc = calculate_ugm3(78.9516, air_avgs[1])
        ugm3_tvoc = calculate_ugm3(60.9516, air_avgs[1])
        ugm3_co2 = calculate_ugm3(44.01, air_avgs[2])
        ugm3_o3 = calculate_ugm3(48.00, air_avgs[3])
        ugm3_o3 = calculate_ugm3(48.00, air_avgs[3])
        #ugm3_co = calculate_ugm3(28.01, air_avgs[4])
        ugm3_co = calculate_ugm3(28.01, co_val)
        #ugm3_pm10 = air_avgs[5]
        ugm3_pm10 = smoke_val

        #final_aqi = (ugm3_co2 * 0.252687954) + (ugm3_tvoc * 0.400181718) + (ugm3_o3 * 0.429166667) + (ugm3_co * 0.00537414966) + (ugm3_pm25 * 1.248920438) + (ugm3_pm10 * 0.740816327)
        #final_aqi = (ugm3_co2 * 0.002526) + (ugm3_tvoc * 0.400181718) + (ugm3_o3 * 0.429166667) + (ugm3_co * 0.00537414966) + (ugm3_pm25 * 1.248920438) + (ugm3_pm10 * 0.740816327)
        final_aqi = (ugm3_co2 * 0.252687954/100) + (ugm3_tvoc * 0.400181718/10) + (ugm3_o3 * 0.429166667) + (ugm3_co * 0.00537414966) + (ugm3_pm25 * 1.248920438) + (ugm3_pm10 * 0.740816327/100.0)


        
        ######aqi_val = air_avgs[0]*1.248920438 + air_avgs[3]*0.429166667 + air_avgs[4]*5.37414966
        #aqi_val = air_avgs[0]*1.248920438 + air_avgs[1]*0.740816327 + air_avgs[2]*0.400181718 + air_avgs[3]*0.429166667
        aqi_val = final_aqi
        aqi_val = round(aqi_val)
        pollutants_units = POLLUTANTS_UNITS
        pollutants_states = []
        bar_colors = []
        bar_vals = []

        # PM2.5
        state, color = get_PM25_state_barColor(pollutants_vals[0])
        pollutants_states.append(state)
        bar_colors.append(color)
        val =  get_barValue(air_avgs[0], PM25_max)
        bar_vals.append(val)


        # TVOC
        state, color = get_VOC_state_barColor(air_avgs[1])
        pollutants_states.append(state)
        bar_colors.append(color)
        val =  get_barValue(air_avgs[1], tVOC_max)
        bar_vals.append(val)

        # CO2
        state, color = get_CO2_state_barColor(air_avgs[2])
        pollutants_states.append(state)
        bar_colors.append(color)
        val =  get_barValue(air_avgs[2], CO2_max)
        bar_vals.append(val)

        # O3
        state, color = get_O3_state_barColor(air_avgs[3])
        pollutants_states.append(state)
        bar_colors.append(color)
        val =  get_barValue(air_avgs[3], O3_max)
        bar_vals.append(val)

        # CO
        #state, color = get_CO_state_barColor(air_avgs[4])
        state, color = get_CO_state_barColor(co_val)
        pollutants_states.append(state)
        bar_colors.append(color)
        #val =  get_barValue(air_avgs[4], CO_max)
        val =  get_barValue(co_val, CO_max)
        bar_vals.append(val)

        # Smoke
        #state, color = get_Smoke_state_barColor(air_avgs[5])
        state, color = get_Smoke_state_barColor(smoke_val)
        pollutants_states.append(state)
        bar_colors.append(color)
        #val =  get_barValue(air_avgs[5], Smoke_max)
        val =  get_barValue(smoke_val, Smoke_max)
        bar_vals.append(val)


        # LPG
        state, color = get_LPG_state_barColor(air_avgs[6])
        pollutants_states.append(state)
        bar_colors.append(color)
        val =  get_barValue(air_avgs[6], LPG_max)
        bar_vals.append(val)

        # NG
        #state, color = get_NG_state_barColor(air_avgs[7])
        state, color = get_NG_state_barColor(ng_val)
        pollutants_states.append(state)
        bar_colors.append(color)


        # GAYATRI
        #air_avgs[7] = 10
        val =  get_barValue(ng_val, NG_max)
        bar_vals.append(val)

        # eCO2
        state, color = get_eCO2_state_barColor(air_avgs[8])
        pollutants_states.append(state)
        bar_colors.append(color)
        val =  get_barValue(air_avgs[8], CO2_max)
        bar_vals.append(val)

        # H2
        state, color = get_H2_state_barColor(air_avgs[9])
        pollutants_states.append(state)
        bar_colors.append(color)
        # PUT H2 MAX
        val =  get_barValue(air_avgs[9], CO_max)
        bar_vals.append(val)


    #t3 = time.time()

    '''
    print ("&&&&&&&&&&&&&&& DD average &&&&&&&&&&&&&&&&&&&&")
    print (t2-t1)
    print (type(airdata))
    print ("start data")
    print (airdata)
    print (t3-t2)
    print ("&&&&&&&&&&&&&&& END DD average &&&&&&&&&&&&&&&&&&&&")
    '''


    #t1 = time.time()
    geo = Air.query.with_entities(
            Air.city,
            Air.state,
            Air.country,
            Air.place
            ).filter(Air.zipcode == zipcode).first()

    if geo:
        location_data = {
            "zipCode": zipcode,
            "city": geo[0],
            "state": geo[1],
            "country": geo[2],
            "place": geo[3]
        }
    else:
        location_data = {
            "zipCode": zipcode,
            "city": "N/A",
            "state": "N/A",
            "country": "N/A",
            "place": "N/A"
        }
    #print ("$$$$$$$$$$$$$$$")
    #print (location_data)
    #print ("$$$$$$$$$$$$$$$")

    #"barColor": bar_colors[i],
    #"barProgress": bar_vals[i],
    pollutants_data = []
    for i in range(10):
        d = {
            "name": POLLUTANTS_NAMES[i],
            "abbr": POLLUTANTS_ABBR[i],
            "value": pollutants_vals[i],
            "units": POLLUTANTS_UNITS[i],
            "state": pollutants_states[i],
            "barProgress": bar_vals[i],
            "barColor": bar_colors[i],
            "tipsTitle": POLLUTANTS_TIPS_TITLES[i],
            "tipsContent": POLLUTANTS_TIPS_CONTENTS[i],
            "order": POLLUTANTS_ORDER[i]
        }
        pollutants_data.append(d)


    weather_data = [
        {
            "name": NAME_TEMP,
            "abbr": ABBR_TEMP,
            "value": weather_vals[0],
            "unit": weather_units[0],
            "order": ORDER_TEMP
        },
        {
            "name": NAME_HUMIDITY,
            "abbr": ABBR_HUMIDITY,
            "value": weather_vals[1],
            "unit": weather_units[1],
            "order": ORDER_HUMIDITY
        },
        {
            "name": NAME_PRESSURE,
            "abbr": ABBR_PRESSURE,
            "value": weather_vals[2],
            "unit": weather_units[2],
            "order": ORDER_PRESSURE
        },
        {
            "name": NAME_ALTITUDE,
            "abbr": ABBR_ALTITUDE,
            "value": weather_vals[3],
            "unit": weather_units[3],
            "order": ORDER_ALTITUDE
        },
    ]
    
    print (pollutants_data)

    data = {
        "pollutantDetails": pollutants_data,
        "weatherDetails": weather_data,
        "locationDetails": location_data,
        "aqi": aqi_val
    }
    print ("DATA DATA DATA")
    print (data)
    print ("DATA DATA DATA")
    return data


# CSV HOURLY DATA HARI hari
def csv_hourly_data(zipcode, num_of_days=ONE_DAY):
    pollutants_vals = ["N/A"] * NUM_OF_POLLLUTANTS
    pollutants_units = [""] * NUM_OF_POLLLUTANTS
    bar_vals = [0] * NUM_OF_POLLLUTANTS
    bar_colors = ["GREEN"] * NUM_OF_POLLLUTANTS
    pollutants_states = ["N/A"] * NUM_OF_POLLLUTANTS
    weather_vals = ["N/A"]*4
    weather_units = [""]*4
    aqi_val = 0

    POLLUTANTS_DATA_AVAILABLE = True
    WEATHER_DATA_AVAILABLE = True

    past_time = datetime.now() - timedelta(days=num_of_days)

    airdata = Air.query.with_entities(
            Air.dustDensity,
            Air.tVOC,
            Air.co2_ppm,
            Air.mq131_o3_ppm,
            Air.mq7_co_ppm,
            Air.mq2_smoke_ppm,
            Air.mq6_lpg_ppm,
            Air.mq4_ng_ppm,
            Air.eCO2,
            Air.mq7_h2_ppm,
            Air.temp,
            Air.humidity,
            Air.pressure,
            Air.altitude,
            ).filter(Air.zipcode == zipcode, Air.timestamp >= past_time).all()

    print (airdata)
    print ("^^^^^^^^^^^^^^^^^^")

    air_avgs = airdata[0]



    total_nones = air_avgs.count(None)
    if total_nones == 14:
        POLLUTANTS_DATA_AVAILABLE = False
        WEATHER_DATA_AVAILABLE = False
    else:
        pollut_nones = air_avgs[:10].count(None)
        weather_nones = air_avgs[10:].count(None)

        if pollut_nones == 10:
            POLLUTANTS_DATA_AVAILABLE = False
        if weather_nones == 4:
            WEATHER_DATA_AVAILABLE = False

    if WEATHER_DATA_AVAILABLE:
        # altitude adjustment
        val = air_avgs[13]
        if zipcode == '94720':
            if  val < 150:
                val = 177.0
            elif  val > 210:
                val = 177.0
        elif zipcode == '95014':
            if  val < 180:
                val = 236.0
            elif  val > 250:
                val = 236.0
        elif zipcode == '95064':
            if  val < 650:
                val = 763.0
            elif  val > 850:
                val = 763.0
        elif zipcode == '96150':
            if  val < 5500:
                val = 6263.0
            elif  val > 6350:
                val = 6263.0
        elif zipcode == '94305':
            if  val < 135:
                val = 141.0
            elif  val > 155:
                val = 141.0

        weather_vals = [air_avgs[10], air_avgs[11], air_avgs[12], val]
        weather_units = WEATHER_UNITS


    if POLLUTANTS_DATA_AVAILABLE:
        lpgval = air_avgs[6]
        while lpgval > 10:
            lpgval = lpgval/10

        ng_val = air_avgs[7]

        co_val = air_avgs[4]/10
        smoke_val = air_avgs[5]/10

        # PM25, tVOC, CO2, O3, CO, Smoke, LPG, NG, eCO2, H2
        pollutants_vals = [air_avgs[0], air_avgs[1], air_avgs[2], air_avgs[3],
                            co_val, smoke_val, lpgval, ng_val,
                            air_avgs[8], air_avgs[9]]

        print (air_avgs)
        print ("------- vals --------")

        # Replacing no2 with co2
        # Replacing so2 with tVOC
        ugm3_pm25 = air_avgs[0]
        ugm3_tvoc = calculate_ugm3(60.9516, air_avgs[1])
        ugm3_co2 = calculate_ugm3(44.01, air_avgs[2])
        ugm3_o3 = calculate_ugm3(48.00, air_avgs[3])
        ugm3_co = calculate_ugm3(28.01, co_val)
        ugm3_pm10 = smoke_val

        final_aqi = (ugm3_co2 * 0.252687954/100) + (ugm3_tvoc * 0.400181718/10) + (ugm3_o3 * 0.429166667) + (ugm3_co * 0.00537414966) + (ugm3_pm25 * 1.248920438) + (ugm3_pm10 * 0.740816327/100.0)

        ######aqi_val = air_avgs[0]*1.248920438 + air_avgs[3]*0.429166667 + air_avgs[4]*5.37414966
        #aqi_val = air_avgs[0]*1.248920438 + air_avgs[1]*0.740816327 + air_avgs[2]*0.400181718 + air_avgs[3]*0.429166667
        aqi_val = final_aqi
        aqi_val = round(aqi_val)
        pollutants_units = POLLUTANTS_UNITS
        pollutants_states = []
        bar_colors = []
        bar_vals = []

        # PM2.5
        state, color = get_PM25_state_barColor(pollutants_vals[0])
        pollutants_states.append(state)
        bar_colors.append(color)
        val =  get_barValue(air_avgs[0], PM25_max)
        bar_vals.append(val)


        # TVOC
        state, color = get_VOC_state_barColor(air_avgs[1])
        pollutants_states.append(state)
        bar_colors.append(color)
        val =  get_barValue(air_avgs[1], tVOC_max)
        bar_vals.append(val)

        # CO2
        state, color = get_CO2_state_barColor(air_avgs[2])
        pollutants_states.append(state)
        bar_colors.append(color)
        val =  get_barValue(air_avgs[2], CO2_max)
        bar_vals.append(val)

        # O3
        state, color = get_O3_state_barColor(air_avgs[3])
        pollutants_states.append(state)
        bar_colors.append(color)
        val =  get_barValue(air_avgs[3], O3_max)
        bar_vals.append(val)

        # CO
        #state, color = get_CO_state_barColor(air_avgs[4])
        state, color = get_CO_state_barColor(co_val)
        pollutants_states.append(state)
        bar_colors.append(color)
        #val =  get_barValue(air_avgs[4], CO_max)
        val =  get_barValue(co_val, CO_max)
        bar_vals.append(val)

        # Smoke
        #state, color = get_Smoke_state_barColor(air_avgs[5])
        state, color = get_Smoke_state_barColor(smoke_val)
        pollutants_states.append(state)
        bar_colors.append(color)
        #val =  get_barValue(air_avgs[5], Smoke_max)
        val =  get_barValue(smoke_val, Smoke_max)
        bar_vals.append(val)


        # LPG
        state, color = get_LPG_state_barColor(air_avgs[6])
        pollutants_states.append(state)
        bar_colors.append(color)
        val =  get_barValue(air_avgs[6], LPG_max)
        bar_vals.append(val)

        # NG
        #state, color = get_NG_state_barColor(air_avgs[7])
        state, color = get_NG_state_barColor(ng_val)
        pollutants_states.append(state)
        bar_colors.append(color)


        # GAYATRI
        #air_avgs[7] = 10
        val =  get_barValue(ng_val, NG_max)
        bar_vals.append(val)

        # eCO2
        state, color = get_eCO2_state_barColor(air_avgs[8])
        pollutants_states.append(state)
        bar_colors.append(color)
        val =  get_barValue(air_avgs[8], CO2_max)
        bar_vals.append(val)

        # H2
        state, color = get_H2_state_barColor(air_avgs[9])
        pollutants_states.append(state)
        bar_colors.append(color)
        # PUT H2 MAX
        val =  get_barValue(air_avgs[9], CO_max)
        bar_vals.append(val)


    geo = Air.query.with_entities(
            Air.city,
            Air.state,
            Air.country,
            Air.place
            ).filter(Air.zipcode == zipcode).first()

    if geo:
        location_data = {
            "zipCode": zipcode,
            "city": geo[0],
            "state": geo[1],
            "country": geo[2],
            "place": geo[3]
        }
    else:
        location_data = {
            "zipCode": zipcode,
            "city": "N/A",
            "state": "N/A",
            "country": "N/A",
            "place": "N/A"
        }
    pollutants_data = []
    for i in range(10):
        d = {
            "name": POLLUTANTS_NAMES[i],
            "abbr": POLLUTANTS_ABBR[i],
            "value": pollutants_vals[i],
            "units": POLLUTANTS_UNITS[i],
            "state": pollutants_states[i],
            "barProgress": bar_vals[i],
            "barColor": bar_colors[i],
            "tipsTitle": POLLUTANTS_TIPS_TITLES[i],
            "tipsContent": POLLUTANTS_TIPS_CONTENTS[i],
            "order": POLLUTANTS_ORDER[i]
        }
        pollutants_data.append(d)


    weather_data = [
        {
            "name": NAME_TEMP,
            "abbr": ABBR_TEMP,
            "value": weather_vals[0],
            "unit": weather_units[0],
            "order": ORDER_TEMP
        },
        {
            "name": NAME_HUMIDITY,
            "abbr": ABBR_HUMIDITY,
            "value": weather_vals[1],
            "unit": weather_units[1],
            "order": ORDER_HUMIDITY
        },
        {
            "name": NAME_PRESSURE,
            "abbr": ABBR_PRESSURE,
            "value": weather_vals[2],
            "unit": weather_units[2],
            "order": ORDER_PRESSURE
        },
        {
            "name": NAME_ALTITUDE,
            "abbr": ABBR_ALTITUDE,
            "value": weather_vals[3],
            "unit": weather_units[3],
            "order": ORDER_ALTITUDE
        },
    ]
    
    print (pollutants_data)

    data = {
        "pollutantDetails": pollutants_data,
        "weatherDetails": weather_data,
        "locationDetails": location_data,
        "aqi": aqi_val
    }
    print ("DATA DATA DATA")
    print (data)
    print ("DATA DATA DATA")
    return data


@app.route('/', methods=['GET'])
def hello_world():
        print ("I DID MAKE IT HERE")
        return 'This is the Air Monitoring REST API site!!!', 200


##@app.before_request
@app.route('/api/air/zipcodes', methods=['GET'])
def zipcodes_data():
    rows = Air.query.with_entities(Air.zipcode).distinct(Air.zipcode)

    all_rows = []
    for row in rows.all():
        all_rows.append(row)
    #all_rows = list(flatten(all_rows))
    #all_rows = ['94305', '95014', '96150']
    #all_rows = ['94305', '95014', '94720', '96150']
    #all_rows = ['94305', '95014', '94720', '95136']
    #all_rows = ['94305', '95014', '94720', '96150', '95064']
    all_rows = ['95014']
    return jsonify(all_rows), 200
    #return jsonify({'zipcodes': all_rows}), 200


@app.route('/api/air/zipcode/<zipcode>/atmosome', methods=['GET'])
def atmosome_data(zipcode):
    #hourly_info = hourly_data(zipcode, 720)
    hourly_info = hourly_data(zipcode)
    cumulative_info = cumulative_exposure_data(zipcode)
    timeseries_info = timeseries_data(zipcode)

    data = {}
    data.update(hourly_info)
    data.update(cumulative_info)
    data.update(timeseries_info)
    
    return jsonify(data), 200

@app.route('/api/air/zipcode/<zipcode>/atmosome/summary', methods=['GET'])
def atmosome_data_summary(zipcode):
    data = hourly_data(zipcode)
    #data = hourly_data(zipcode, 720)

    return jsonify(data), 200


@app.route('/api/air/zipcode/<zipcode>/atmosome/cumulative', methods=['GET'])
def atmosome_data_cumulative(zipcode):
    data = cumulative_exposure_data(zipcode)

    return jsonify(data), 200

@app.route('/api/air/zipcode/<zipcode>/atmosome/timeseries', methods=['GET'])
def atmosome_data_timeseries(zipcode):
    data = timeseries_data(zipcode)

    return jsonify(data), 200

@app.route('/api/air/atmosome/html/<parameter>', methods=['GET'])
def read_html_static_page(parameter):
    filename = "{}/{}.html".format(app.config["CLIENT_TEMPLATES"], parameter)
    with open(filename, 'r') as f:
        content =f.read()
        data = {
                "content": content
                }

    return jsonify(data), 200

@app.route('/api/air/zipcode/<zipcode>/24hours', methods=['GET'])
def zipcode_24hours_data(zipcode):
  if request.method == 'GET':

    time_24_hours_ago = datetime.datetime.now() - datetime.timedelta(days=1)
    airs = Air.query.filter(Air.zipcode == zipcode, Air.timestamp__gte==time_24_hours_ago).all()
    air_schema = AirSchema(many=True)
    output = air_schema.dump(airs).data

    print (type(output))
    print (output[0])
    num_of_records = len(output)
    print (num_of_records)


    return jsonify({'airs': message}), 200


@app.route('/api/air', methods=['GET','POST'])
def data():
  if request.method == 'POST':
    print ("HERE HERE HERE HERE")
    print ("Inside data method in post")
    #print ("Will print data received")
    data_elements = request.get_json(force=True) 
    print ("<<<<<<<<>>>>>>>>>>>>>")
    print (data_elements)
    print ("<<<<<<<<>>>>>>>>>>>>>")
    #print ("printed data received")
    #print ("\n")
    date_str = data_elements.get("date_time")

    mq2_raw = float(data_elements['mq2_raw'])
    mq2_ref_lpg_ppm  = calculate_on_ref_Ro(mq2_raw,
                        MQ2_RL,
                        MQ2_Ref_Ro,
                        MQ2_LPGCurve
                       )
    #print ("mq2 LPG: old: 0 ppm new: {0:.4f} ppm".format(mq2_ref_lpg_ppm))

    mq2_ref_co_ppm  = calculate_on_ref_Ro(mq2_raw,
                        MQ2_RL,
                        MQ2_Ref_Ro,
                        MQ2_COCurve
                       )
    #print ("mq2 CO: old: 0 ppm new: {0:.4f} ppm".format(mq2_ref_co_ppm))

    mq2_ref_smoke_ppm  = calculate_on_ref_Ro(mq2_raw,
                        MQ2_RL,
                        MQ2_Ref_Ro,
                        MQ2_SmokeCurve
                       )
    #print ("mq2 SMOKE: old: 0 ppm new: {0:.4f} ppm".format(mq2_ref_smoke_ppm))

    mq4_raw = float(data_elements['mq4_raw'])
    mq4_ref_ng_ppm  = calculate_on_ref_Ro(mq4_raw,
                        MQ4_RL,
                        MQ4_Ref_Ro,
                        MQ4_MethaneCurve
                       )
    #print ("mq4 NG: old: 0 ppm new: {0:.4f} ppm".format(mq4_ref_ng_ppm))

    mq6_raw = float(data_elements['mq6_raw'])
    mq6_ref_lpg_ppm  = calculate_on_ref_Ro(mq6_raw,
                        MQ6_RL,
                        MQ6_Ref_Ro,
                        MQ6_LPGCurve
                       )
    #print ("mq6 LPG: old: 0 ppm new: {0:.4f} ppm".format(mq6_ref_lpg_ppm))

    mq7_raw = float(data_elements['mq7_raw'])
    mq7_ref_co_ppm  = calculate_on_ref_Ro(mq7_raw,
                        MQ7_RL,
                        MQ7_Ref_Ro,
                        MQ7_COCurve
                       )
    #print ("mq7: old CO: 0 ppm new CO: {0:.4f} ppm".format(mq7_ref_co_ppm))

    mq7_ref_h2_ppm  = calculate_on_ref_Ro(mq7_raw,
                        MQ7_RL,
                        MQ7_Ref_Ro,
                        MQ7_H2Curve
                       )
    #print ("mq7: old H2: 0 ppm new H2: {0:.4f} ppm".format(mq7_ref_h2_ppm))

    try:
        mq131_raw = float(data_elements['mq131'])
    except KeyError as e:
        mq131_raw = float(data_elements['mq131_raw'])

    mq131_ref_o3_ppm  = calculate_on_ref_Ro(mq131_raw,
                        MQ131_RL,
                        MQ131_Ref_Ro,
                        MQ131_O3Curve
                       )
    #print ("mq131: old: 0 ppm new: {0:.4f} ppm".format(mq131_ref_o3_ppm))

    zipcode=data_elements['zipcode']
    altitude=float(data_elements['altitude'])
    temp=float(data_elements['temp'])
    mq4_ng_ppm=float(data_elements['mq4_ng_ppm'])

    if zipcode == '94720':
        if  altitude < 150:
            altitude = 177.0
        elif  altitude > 210:
            altitude = 177.0

        if mq4_ng_ppm > 100:
            mq4_ng_ppm = mq4_ng_ppm/100
    elif zipcode == '95014':
        if  altitude < 180:
            altitude = 236.0
        elif  altitude > 250:
            altitude = 236.0
    elif zipcode == '95064':
        if  altitude < 650:
            altitude = 763.0
        elif  altitude > 850:
            altitude = 763.0
        temp = temp-5
    elif zipcode == '96150':
        if  altitude < 5500:
            altitude = 6263.0
        elif  altitude > 6350:
            altitude = 6263.0
    elif zipcode == '94305':
        if  altitude < 135:
            altitude = 141.0
        elif  altitude > 155:
            altitude = 141.0

    # hari redo co2 for blau lab
    co2_raw=float(data_elements['co2_raw'])
    co2_ppm=float(data_elements['co2_ppm'])


    if zipcode == '94305':
        concentration = co2_raw * 8
        #concentration = concentration/1.5;

        if concentration < 0:
            print ("Not adjusting co2ppm.")
        else:
            print ("concentration: {}".format(concentration))

            if concentration > 600:
                concentration = (concentration * 1.5)/1.4
            elif concentration > 1000:
                concentration = (concentration * 1.5)/1.3

            co2_raw = co2_ppm
            co2_ppm = concentration

            print ("co2_ppm: {}".format(co2_ppm))
            print ("END HARI ADJUSTED BLAU LAB CO2 END") 




    if date_str:
        T_idx = date_str.find("T")
        if T_idx >= 0:
            datetime_obj = create_datetime_obj(date_str, delimiter="T")
        else:
            datetime_obj = create_datetime_obj(date_str)


        #temp=float(data_elements['temp']),
        air = Air(
            timestamp = datetime_obj,
            city=data_elements['city'],
            state=data_elements['state'],
            country=data_elements['country'],
            #zipcode=data_elements['zipcode'],
            zipcode=zipcode,
            place=data_elements['place'],
            details=data_elements['details'],
            misc=data_elements['misc'],
            tVOC=float(data_elements['tVOC']),
            eCO2=float(data_elements['eCO2']),
            temp=temp,
            pressure=float(data_elements['pressure']),
            #altitude=float(data_elements['altitude']),
            altitude=altitude,
            humidity=float(data_elements['humidity']),
            mq2_raw=mq2_raw,
            mq2_ro=float(data_elements['mq2_ro']),
            mq2_rs_by_ro=float(data_elements['mq2_rs_by_ro']),
            mq2_lpg_ppm=float(data_elements['mq2_lpg_ppm']),
            mq2_co_ppm=float(data_elements['mq2_co_ppm']),
            mq2_smoke_ppm=float(data_elements['mq2_smoke_ppm']),
            mq2_ref_ro=MQ2_Ref_Ro,
            mq2_ref_lpg_ppm=mq2_ref_lpg_ppm,
            mq2_ref_co_ppm=mq2_ref_co_ppm,
            mq2_ref_smoke_ppm=mq2_ref_smoke_ppm,
            mq4_raw=mq4_raw,
            mq4_ro=float(data_elements['mq4_ro']),
            mq4_rs_by_ro=float(data_elements['mq4_rs_by_ro']),
            #mq4_ng_ppm=float(data_elements['mq4_ng_ppm']),
            mq4_ng_ppm=mq4_ng_ppm,
            mq4_ng_ppm2=float(data_elements['mq4_ng_ppm2']),
            mq4_ref_ro=MQ4_Ref_Ro,
            mq4_ref_ng_ppm=mq4_ref_ng_ppm,
            mq6_raw=mq6_raw,
            mq6_ro=float(data_elements['mq6_ro']),
            mq6_rs_by_ro=float(data_elements['mq6_rs_by_ro']),
            mq6_lpg_ppm=float(data_elements['mq6_lpg_ppm']),
            mq6_lpg_ppm2=float(data_elements['mq6_lpg_ppm2']),
            mq6_ref_ro=MQ6_Ref_Ro,
            mq6_ref_lpg_ppm=mq6_ref_lpg_ppm,
            mq7_raw=mq7_raw,
            mq7_ro=float(data_elements['mq7_ro']),
            mq7_rs_by_ro=float(data_elements['mq7_rs_by_ro']),
            mq7_co_ppm=float(data_elements['mq7_co_ppm']),
            mq7_h2_ppm=float(data_elements['mq7_h2_ppm']),
            mq7_co_ppm2=float(data_elements['mq7_co_ppm2']),
            mq7_ref_ro=MQ7_Ref_Ro,
            mq7_ref_co_ppm=mq7_ref_co_ppm,
            mq7_ref_h2_ppm=mq7_ref_h2_ppm,
            mq131_raw=mq131_raw,
            mq131_ro=float(data_elements['mq131_ro']),
            mq131_rs_by_ro=float(data_elements['mq131_rs_by_ro']),
            mq131_o3_ppm=float(data_elements['mq131_o3_ppm']),
            mq131_o3_ppm2=float(data_elements['mq131_o3_ppm2']),
            mq131_ref_ro=MQ131_Ref_Ro,
            mq131_ref_o3_ppm=mq131_ref_o3_ppm,
            #co2_raw=float(data_elements['co2_raw']),
            #co2_ppm=float(data_elements['co2_ppm']),
            co2_raw=co2_raw,
            co2_ppm=co2_ppm,
            dust_raw=float(data_elements['dust_raw']),
            dust_Vo=float(data_elements['dust_Vo']),
            dust_Voc=float(data_elements['dust_Voc']),
            dust_dV=float(data_elements['dust_dV']),
            dust_Vo_mV=float(data_elements['dust_Vo_mV']),
            dustDensity=float(data_elements['dustDensity']),
        )
    else:
        print ("-------")
        print (data_elements['eCO2'])
        print ("---------")
        air = Air(
            city=data_elements['city'],
            state=data_elements['state'],
            country=data_elements['country'],
            #zipcode=data_elements['zipcode'],
            zipcode=zipcode,
            place=data_elements['place'],
            details=data_elements['details'],
            misc=data_elements['misc'],
            tVOC=float(data_elements['tVOC']),
            eCO2=float(data_elements['eCO2']),
            #temp=float(data_elements['temp']),
            temp=temp,
            pressure=float(data_elements['pressure']),
            #altitude=float(data_elements['altitude']),
            altitude=altitude,
            humidity=float(data_elements['humidity']),
            mq2_raw=mq2_raw,
            mq2_ro=float(data_elements['mq2_ro']),
            mq2_rs_by_ro=float(data_elements['mq2_rs_by_ro']),
            mq2_lpg_ppm=float(data_elements['mq2_lpg_ppm']),
            mq2_co_ppm=float(data_elements['mq2_co_ppm']),
            mq2_smoke_ppm=float(data_elements['mq2_smoke_ppm']),
            mq2_ref_ro=MQ2_Ref_Ro,
            mq2_ref_lpg_ppm=mq2_ref_lpg_ppm,
            mq2_ref_co_ppm=mq2_ref_co_ppm,
            mq2_ref_smoke_ppm=mq2_ref_smoke_ppm,
            mq4_raw=mq4_raw,
            mq4_ro=float(data_elements['mq4_ro']),
            mq4_rs_by_ro=float(data_elements['mq4_rs_by_ro']),
            #mq4_ng_ppm=float(data_elements['mq4_ng_ppm']),
            mq4_ng_ppm=mq4_ng_ppm,
            mq4_ng_ppm2=float(data_elements['mq4_ng_ppm2']),
            mq4_ref_ro=MQ4_Ref_Ro,
            mq4_ref_ng_ppm=mq4_ref_ng_ppm,
            mq6_raw=mq6_raw,
            mq6_ro=float(data_elements['mq6_ro']),
            mq6_rs_by_ro=float(data_elements['mq6_rs_by_ro']),
            mq6_lpg_ppm=float(data_elements['mq6_lpg_ppm']),
            mq6_lpg_ppm2=float(data_elements['mq6_lpg_ppm2']),
            mq6_ref_ro=MQ6_Ref_Ro,
            mq6_ref_lpg_ppm=mq6_ref_lpg_ppm,
            mq7_raw=mq7_raw,
            mq7_ro=float(data_elements['mq7_ro']),
            mq7_rs_by_ro=float(data_elements['mq7_rs_by_ro']),
            mq7_co_ppm=float(data_elements['mq7_co_ppm']),
            mq7_h2_ppm=float(data_elements['mq7_h2_ppm']),
            mq7_co_ppm2=float(data_elements['mq7_co_ppm2']),
            mq7_ref_ro=MQ7_Ref_Ro,
            mq7_ref_co_ppm=mq7_ref_co_ppm,
            mq7_ref_h2_ppm=mq7_ref_h2_ppm,
            mq131_raw=mq131_raw,
            mq131_ro=float(data_elements['mq131_ro']),
            mq131_rs_by_ro=float(data_elements['mq131_rs_by_ro']),
            mq131_o3_ppm=float(data_elements['mq131_o3_ppm']),
            mq131_o3_ppm2=float(data_elements['mq131_o3_ppm2']),
            mq131_ref_ro=MQ131_Ref_Ro,
            mq131_ref_o3_ppm=mq131_ref_o3_ppm,
            #co2_raw=float(data_elements['co2_raw']),
            #co2_ppm=float(data_elements['co2_ppm']),
            co2_raw=co2_raw,
            co2_ppm=co2_ppm,
            dust_raw=float(data_elements['dust_raw']),
            dust_Vo=float(data_elements['dust_Vo']),
            dust_Voc=float(data_elements['dust_Voc']),
            dust_dV=float(data_elements['dust_dV']),
            dust_Vo_mV=float(data_elements['dust_Vo_mV']),
            dustDensity=float(data_elements['dustDensity']),
        )

    #try:
    db.session.add(air)
    db.session.commit()
    print ("COMMIT WENT FINE")
    #except Exception as e:
    #    print (e)
    #    print ("OMG I HIT A STUPID EXCEPTION")
        #//sqlite3.OperationalError:
    #    time.sleep(random.randint(10, 30))
    #data, code = create(air)
    air_schema = AirSchema()
    print ("-------------")
    print ("-------------")
    print ("-------------")
    print (air_schema)
    print ("-------------")
    print (air_schema.dump(air))
    print ("-------------")
    print ("-------------")
    print ("-------------")

    output = air_schema.dump(air).get("data")
    return jsonify({'air': output}), 201
  elif request.method == 'GET':
    print (request.url)
    fname = str(datetime.utcnow())
    fname = "{}.json".format(fname)
    print ("*********************** GB *************")
    print (fname)
    print ("*********************** GB *************")
    #return jsonify({'airs': fname}), 200

    # Create the list of air from our data
    airs = Air.query.order_by(Air.timestamp).all()

    air_schema = AirSchema(many=True)
    output = air_schema.dump(airs).data
    print (type(output))
    print (output[0])
    num_of_records = len(output)
    print (num_of_records)
    if (num_of_records > 100):
        fname = datetime.utcnow()
        json_fname = "{}.json".format(fname)
        json_fname = json_fname.replace(" ", "_")
        print ("I AM HERE")
        print (json_fname)
        json_file_with_dir_name = "{}/{}".format(app.config["CLIENT_CSVS"], json_fname) 
        print ("*********************** GB *************")
        print (json_fname)
        print (json_file_with_dir_name)
        print ("*********************** GB *************")

        csv_fname = "{}.csv".format(fname)
        csv_fname = csv_fname.replace(" ", "_")
        csv_file_with_dir_name = "{}/{}".format(app.config["CLIENT_CSVS"], csv_fname)
        print ("*********************** GB *************")
        print (csv_fname)
        print (csv_file_with_dir_name)
        print ("*********************** GB *************")
        csv_columns = ["air_id", "timestamp", "city", "state", "country", "zipcode", "place", "details", "misc", "tVOC", "eCO2", "temp", "pressure", "altitude", "humidity", "mq2_smoke_ppm", "mq4_ng_ppm", "mq6_lpg_ppm", "mq7_co_ppm", "mq131_o3_ppm", "co2_ppm", "dustDensity"]
        with open(csv_file_with_dir_name, 'a+') as outfile:
            wr = csv.DictWriter(outfile, fieldnames=csv_columns, dialect='excel')
            wr.writeheader()
            for record in output:
                wr.writerow(record)

        with open(json_file_with_dir_name, 'a+') as outfile:
            outfile.write(json.dumps(output))
            outfile.write("\n")

        csv_url = "{}/downloads/{}".format(request.url, csv_fname)
        json_url = "{}/downloads/{}".format(request.url, json_fname)
        message = ("Your query resulted in {} records. "
                   "This is too much data to embed in this result. "
                   "Please download the json file pasting this url in the browser: "
                   "{}"
                   " Or, download the file in csv format by pasting this link in the browser: "
                   "{}"
                   ).format(num_of_records, json_url, csv_url)
        return jsonify({'airs': message}), 200
    else:
        return jsonify({'airs': output}), 200

    return jsonify({'airs': "Data has been saved on server"}), 200

@app.route('/api/air/downloads_deprecated/<filename>', methods=['GET'])
def data_by_json_file(filename):
    try:
        return send_from_directory(app.config["CLIENT_CSVS"],
                                   filename=filename,
                                   as_attachment=True)
    except FileNotFoundError:
        abort(404)

#https://atm-rest.com/api/air/zipcode/95014/timeseries/csv/downloads/2020-12-08_04:13:49.978951.csv
@app.route('/api/air/<zipcode>/timeseries/csv/downloads/<filename>', methods=['GET'])
def data_by_csv_file(filename):
    try:
        return send_from_directory(app.config["CLIENT_CSVS"],
                                   filename=filename,
                                   as_attachment=True)
    except FileNotFoundError:
        abort(404)

@app.route('/api/air/zipcode/<zipcode>/pollutants', methods=['GET'])
def data_pollutants_by_zipcode(zipcode):
  print ("I AM HERE")
  if request.method == 'GET':

    pollutants = {
                    "tVOC": 10,
                    "eCO2": 10,
                    "smoke": 10,
                    "ng": 10,
                    "lpg": 10,
                    "co": 10,
                    "h2": 10,
                    "o3": 10,
                    "co2": 10,
                    "pm2.5": 10
                    }
    metrics = {
                 "temperature": 10,
                 "pressure": 10,
                 "altitude": 10,
                 "humidity": 10,
                 "city": "city",
                 "state": "state",
                 "country": "country",
              }
            
    data = {"details": metrics, "pollutants": pollutants}
    return jsonify({'data': data}), 200

@app.route('/api/air/zipcode/<zipcode>', methods=['GET'])
def data_by_zipcode(zipcode):
  if request.method == 'GET':
    airs = Air.query.filter(Air.zipcode == zipcode).all()
    air_schema = AirSchema(many=True)
    output = air_schema.dump(airs).data
    return jsonify({'airs': output}), 200

@app.route('/api/air/zipcode/<zipcode>/stanford/download', methods=['GET'])
def data_by_zipcode_download_csv(zipcode):
  if request.method == 'GET':
    airs = Air.query.filter(Air.zipcode == zipcode).all()
    #air_schema = AirSchema(many=True)
    #output = air_schema.dump(airs)
    #output = air_schema.dump(airs)
    print (airs[0])
    print (airs[0].mq2_raw)

    
    print ("JEEEEEEEEEEEEESSSSSSSSSSSIIIIII")



    num_of_records = len(airs)
    print (num_of_records)
    raws = [air.mq2_raw for air in airs]
    ppms = [air.mq2_smoke_ppm for air in airs]
    
    data = {"raws": raws, "ppms": ppms}
    return jsonify({'data': data}), 200



    fname = datetime.utcnow()
    csv_fname = "{}_{}.csv".format(fname, zipcode)
    csv_fname = csv_fname.replace(" ", "_")
    csv_file_with_dir_name = "{}/{}".format(app.config["CLIENT_CSVS"], csv_fname)
    print ("*********************** GB *************")
    print (csv_fname)
    print (csv_file_with_dir_name)
    print ("*********************** GB *************")
    csv_columns = ["air_id", "timestamp", "city", "state", "country", "zipcode", "place", "details", "misc", "tVOC", "eCO2", "temp", "pressure", "altitude", "humidity", "mq2_smoke_ppm", "mq4_ng_ppm", "mq6_lpg_ppm", "mq7_co_ppm", "mq131_o3_ppm", "co2_ppm", "dustDensity"]

    with open(csv_file_with_dir_name, 'a+') as outfile:
        wr = csv.DictWriter(outfile, fieldnames=csv_columns, dialect='excel')
        wr.writeheader()
        for record in airs:
            wr.writerow(record)


    current_url = request.url
    urls = current_url.split("zipcode")
    parent_url = urls[0]

    csv_url = "{}downloads/{}".format(parent_url, csv_fname)
    message = ("Your query for zipcode {} resulted in {} records. "
               "Please download your data as a csv file pasting this url in the browser: "
               "{}"
               ).format(zipcode, num_of_records, csv_url)
    return jsonify({'airs': message}), 200


@app.route('/api/air/country/<country>', methods=['GET'])
def data_by_country(country):
  if request.method == 'GET':
    airs = Air.query.filter(Air.country == country).all()
    air_schema = AirSchema(many=True)
    output = air_schema.dump(airs).data
    return jsonify({'airs': output}), 200

@app.route('/api/air/country/<country>/state/<state>', methods=['GET'])
def data_by_country_state(country, state):
  if request.method == 'GET':
    airs = Air.query.filter(Air.country == country).filter(Air.state == state).all()
    air_schema = AirSchema(many=True)
    output = air_schema.dump(airs).data
    return jsonify({'airs': output}), 200

@app.route('/api/air/country/<country>/state/<state>/city/<city>', methods=['GET'])
def data_by_country_state_city(country, state, city):
  if request.method == 'GET':
    airs = Air.query.filter(Air.country == country).filter(Air.state == state).filter(Air.city == city).all()
    air_schema = AirSchema(many=True)
    output = air_schema.dump(airs).data
    return jsonify({'airs': output}), 200

@app.route('/api/air/start_date/<start_date>', methods=['GET'])
def data_from_startdate(start_date):
  if request.method == 'GET':
    start = parse_date(start_date)
    airs = Air.query.filter(Air.timestamp >= start)
    air_schema = AirSchema(many=True)
    output = air_schema.dump(airs).data
    return jsonify({'airs': output}), 200

@app.route('/api/air/end_date/<end_date>', methods=['GET'])
def data_until_enddate(end_date):
  if request.method == 'GET':
    end = parse_date(end_date)

    airs = Air.query.filter(Air.timestamp <= end)
    air_schema = AirSchema(many=True)
    output = air_schema.dump(airs).data
    return jsonify({'airs': output}), 200

@app.route('/api/air/start_date/<start_date>/end_date/<end_date>', methods=['GET'])
def data_between_startdate_enddate(start_date, end_date):
  if request.method == 'GET':
    start = parse_date(start_date)
    end = parse_date(end_date)

    airs = Air.query.filter(Air.timestamp >= start)
    airs = Air.query.filter(Air.timestamp <= end).filter(Air.timestamp >= start)
    air_schema = AirSchema(many=True)
    output = air_schema.dump(airs).data
    return jsonify({'airs': output}), 200


if __name__ == "__main__":
    print ("$$$$$$$$$$$$$$$$$")
   #ß app.run(host="0.0.0.0", port=8080, ssl_context=('/etc/letsencrypt/live/atm-rest.com/fullchain.pem', '/etc/letsencrypt/live/atm-rest.com/privkey.pem'))
    app.run(host="0.0.0.0", port=8080)

