from flask import Flask, jsonify, render_template, request , Blueprint
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

print("Switched to:", matplotlib.get_backend())
import pandas as pd
import matplotlib.dates as mdates
from matplotlib.dates import MO, TU, WE, TH, FR, SA, SU
from flask import Response, redirect, request, url_for

print("P1")
# ----------

# app = connexion.FlaskApp(__name__, specification_dir='./')  # or e.g. Flask(__name__, template_folder='../otherdir')

from config import app

# app = Flask(__name__)
# Talisman(app)

# Read the swagger.yml file to configure the endpoints
# app.add_api('air.yml')

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
print("P2")

MQ2_LPGCurve = [2.3, 0.21, -0.47]
MQ2_COCurve = [2.3, 0.72, -0.34]
MQ2_SmokeCurve = [2.3, 0.53, -0.44]
MQ4_MethaneCurve = [2.254, -0.224, -0.077]
MQ6_LPGCurve = [2.301, 0.307, -0.422]
MQ7_COCurve = [1.699, 0.201, -0.651]
MQ7_H2Curve = [1.699, 0.087, -0.729]
MQ131_O3Curve = [0.692, 0.608, -0.900]

DAYS = "days"
HOURS = "hours"
ONE_HOUR = 1
ONE_DAY = 1
ONE_WEEK = 7
ONE_MONTH = 30
TWO_MONTH = 60
THREE_MONTH = 90
# TIMESERIES_QUARTER = 90
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

    df = pd.DataFrame(airdata,
                      columns=['timestamp', 'city', 'state', 'country', 'zipcode', 'place', 'details', 'misc', 'temp',
                               'humidity', 'pressure', 'altitude', 'pm2_5', 'tVOC', 'co2', 'o3', 'co', 'pm10', 'eCO2',
                               'lpg', 'ng', 'h2'])
    t2 = time.time()

    # csv_columns = ["air_id", "timestamp", "city", "state", "country", "zipcode", "place", "details", "misc", "tVOC", "eCO2", "temp", "pressure", "altitude", "humidity", "mq2_smoke_ppm", "mq4_ng_ppm", "mq6_lpg_ppm", "mq7_co_ppm", "mq131_o3_ppm", "co2_ppm", "dustDensity"]

    # data_pm25.loc[data_pm25['PM2.5'] > 40, 'PM2.5'] = 40

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

    df['co'] = df['co'] / 10
    df['pm10'] = df['pm10'] / 10

    print("%%%%%%%%%%%%%% NEW DF %%%%%%%%%%%")
    fname = datetime.utcnow()
    csv_fname = "{}.csv".format(fname)
    csv_fname = csv_fname.replace(" ", "_")
    csv_file_with_dir_name = "{}/{}".format(app.config["CLIENT_CSVS"], csv_fname)
    print("*********************** GB *************")
    print(csv_fname)
    print(csv_file_with_dir_name)
    csv_url = "{}/downloads/{}".format(request.url, csv_fname)
    print("*********************** GB *************")
    df.to_csv(csv_file_with_dir_name, index=False, header=True)

    print(t2 - t1)

    print("####### URLS request.url, csv_filename, csv_url ########")
    print(request.url)
    print(csv_fname)
    print(csv_url)
    print("%%%%%%%%%%%%%% END DF %%%%%%%%%%%")

    '''
        message = ("Please download the file in csv format by pasting this link in the browser: "
                   "{}"
                   ).format(csv_url)
        return jsonify({'air_data_csv_file': message}), 200
        '''

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
    print("^%^%^%^%^%^%^%^%^%^%")
    print("ENTER plot_timeseries")
    print("^%^%^%^%^%^%^%^%^%^%")

    fig, ax = plt.subplots(figsize=(25, 7))

    num_of_data_points = data[data.columns[0]].count()
    print("num_of_data_points")
    print(num_of_data_points)

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
    # loc = mdates.WeekdayLocator(byweekday=(MO,FR))

    if num_of_data_points < 1000:
        loc = mdates.WeekdayLocator(byweekday=(MO, FR))
    elif num_of_data_points < 2000:
        loc = mdates.WeekdayLocator(byweekday=(MO))
    elif num_of_data_points < 3000:
        loc = mdates.WeekdayLocator(byweekday=MO, interval=2)
    else:
        loc = mdates.WeekdayLocator(byweekday=MO, interval=3)
    print("LOC LOC LOC")
    print(loc)
    print("LOC LOC LOC")
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
    print("^%^%^%^%^%^%^%^%^%^%")
    print("Exiting plot_timeseries")
    print(graph_url)
    print("^%^%^%^%^%^%^%^%^%^%")
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
    # past_time = cur_date - timedelta(days=num_of_days)

    t1 = time.time()

    airdata = Air.query.with_entities(
        Air.timestamp,
        Air.mq2_smoke_ppm
    ).filter(Air.zipcode == zipcode, Air.timestamp >= past_time).all()

    t2 = time.time()
    print("%% AIR DATA FOR TIMESERIES  HERE ENTER %%")
    print("airdata: {}".format(airdata))
    print("%% AIR DATA FOR TIMESERIES EXIT if NONE %%")

    if not airdata:
        return {}

    print("%%%%%%%%%%%%%% TS %%%%%%%%%%%")
    # print (t2-t1)
    # print ("airData[0]: ")
    # print (airdata[0])
    # print (airdata[1])
    # print (airdata[2])
    # print (airdata[3])
    print("%%%%%%%%%%%%%% END TS %%%%%%%%%%%")

    t1 = time.time()
    air_zip = zip(*airdata)

    tmp_air_list = list(air_zip)
    air_ts = tmp_air_list[:]

    print(type(air_ts))
    print(air_ts)
    t2 = time.time()
    print("%%%%%%%%%%%%%% TRANSPOSE %%%%%%%%%%%")
    print(t2 - t1)
    print(len(air_ts))
    print("%%%%%%%%%%%%%% END TRANSPOSE %%%%%%%%%%%")

    t1 = time.time()

    l_time = air_ts[0]

    # print ("------- pm25 ------------")
    l_pm10 = air_ts[1]
    d_pm10 = {"timestamp": l_time, "PM10": l_pm10}
    data_pm10 = pd.DataFrame(d_pm10)
    data_pm10["timestamp"] = pd.to_datetime(data_pm10["timestamp"])
    data_pm10.set_index('timestamp', inplace=True)
    thresholds_pm10 = thresholds["pm10"]["lines"]
    graph_pm10 = plot_timeseries(data_pm10, ABBR_SMOKE, UNITS_SMOKE, zipcode,
                                 cur_time, thresholds_pm10)

    t2 = time.time()
    print("^^^^^^^^^^ DATA READINESS ^^^^^^^^^")
    print(t2 - t1)
    print("^^^^^^^^^^ END DATA READINESS ^^^^^^^^^")

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
    # past_time = cur_date - timedelta(days=num_of_days)

    t1 = time.time()

    airdata = Air.query.with_entities(
        Air.timestamp,
        Air.mq4_ng_ppm
    ).filter(Air.zipcode == zipcode, Air.timestamp >= past_time).all()

    t2 = time.time()
    print("%% AIR DATA FOR TIMESERIES  HERE ENTER %%")
    print("airdata: {}".format(airdata))
    print("%% AIR DATA FOR TIMESERIES EXIT if NONE %%")

    if not airdata:
        return {}

    print("%%%%%%%%%%%%%% TS %%%%%%%%%%%")
    # print (t2-t1)
    # print ("airData[0]: ")
    # print (airdata[0])
    # print (airdata[1])
    # print (airdata[2])
    # print (airdata[3])
    print("%%%%%%%%%%%%%% END TS %%%%%%%%%%%")

    t1 = time.time()
    air_zip = zip(*airdata)

    tmp_air_list = list(air_zip)
    air_ts = tmp_air_list[:]

    print(type(air_ts))
    print(air_ts)
    t2 = time.time()
    print("%%%%%%%%%%%%%% TRANSPOSE %%%%%%%%%%%")
    print(t2 - t1)
    print(len(air_ts))
    print("%%%%%%%%%%%%%% END TRANSPOSE %%%%%%%%%%%")

    t1 = time.time()

    l_time = air_ts[0]

    # print ("------- pm25 ------------")
    l_ng = air_ts[1]
    d_ng = {"timestamp": l_time, "NG": l_ng}
    data_ng = pd.DataFrame(d_ng)
    data_ng["timestamp"] = pd.to_datetime(data_ng["timestamp"])
    data_ng.set_index('timestamp', inplace=True)
    thresholds_ng = thresholds["ng"]["lines"]
    graph_ng = plot_timeseries(data_ng, ABBR_NG, UNITS_NG, zipcode,
                               cur_time, thresholds_ng)

    t2 = time.time()
    print("^^^^^^^^^^ DATA READINESS ^^^^^^^^^")
    print(t2 - t1)
    print("^^^^^^^^^^ END DATA READINESS ^^^^^^^^^")

    data = {
        "ts_ng": graph_ng
    }

    return data



@app.route('/', methods=['GET'])
def hello_world():
    print("I DID MAKE IT HERE")
    return 'This is the Air Monitoring REST API site!!!', 200


##@app.before_request
@app.route('/api/air/zipcodes', methods=['GET'])
def zipcodes_data():
    rows = Air.query.with_entities(Air.zipcode).distinct(Air.zipcode)

    all_rows = []
    for row in rows.all():
        all_rows.append(row)
    # all_rows = list(flatten(all_rows))
    # all_rows = ['94305', '95014', '96150']
    # all_rows = ['94305', '95014', '94720', '96150']
    # all_rows = ['94305', '95014', '94720', '95136']
    # all_rows = ['94305', '95014', '94720', '96150', '95064']
    all_rows = ['95014']
    return jsonify(all_rows), 200
    # return jsonify({'zipcodes': all_rows}), 200


@app.route('/api/air/zipcode/<zipcode>/atmosome', methods=['GET'])
def atmosome_data(zipcode):
    # hourly_info = hourly_data(zipcode, 720)
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
    # data = hourly_data(zipcode, 720)

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
        content = f.read()
        data = {
            "content": content
        }

    return jsonify(data), 200


@app.route('/api/air/zipcode/<zipcode>/24hours', methods=['GET'])
def zipcode_24hours_data(zipcode):
    if request.method == 'GET':
        time_24_hours_ago = datetime.datetime.now() - datetime.timedelta(days=1)
        airs = Air.query.filter(Air.zipcode == zipcode, Air.timestamp__gte == time_24_hours_ago).all()
        air_schema = AirSchema(many=True)
        output = air_schema.dump(airs).data

        print(type(output))
        print(output[0])
        num_of_records = len(output)
        print(num_of_records)

        return jsonify({'airs': message}), 200




# https://atm-rest.com/api/air/zipcode/95014/timeseries/csv/downloads/2020-12-08_04:13:49.978951.csv
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
    print("I AM HERE")
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






if __name__ == "__main__":
    print("$$$$$$$$$$$$$$$$$")
    # ß app.run(host="0.0.0.0", port=8080, ssl_context=('/etc/letsencrypt/live/atm-rest.com/fullchain.pem', '/etc/letsencrypt/live/atm-rest.com/privkey.pem'))
    app.run(host="0.0.0.0", port=8080)

