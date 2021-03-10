from flask import Blueprint, render_template
from config import app
from flask import send_file, send_from_directory, safe_join, abort
graph = Blueprint("graph",__name__,static_folder="static",template_folder="templates")



@graph.route('/api/air/zipcode/<zipcode>/timeseries/graphs', methods=['GET'])
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
    # past_time = cur_date - timedelta(days=num_of_days)

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
    l_pm25 = air_ts[1]
    d_pm25 = {"timestamp": l_time, "PM2.5": l_pm25}
    data_pm25 = pd.DataFrame(d_pm25)
    data_pm25.loc[data_pm25['PM2.5'] > 40, 'PM2.5'] = 40
    data_pm25["timestamp"] = pd.to_datetime(data_pm25["timestamp"])
    data_pm25.set_index('timestamp', inplace=True)
    thresholds_pm25 = thresholds["pm25"]["lines"]
    graph_pm25 = plot_timeseries(data_pm25, ABBR_PM25, UNITS_PM25, zipcode,
                                 cur_time, thresholds_pm25)

    # print ("------- tVOC ------------")
    l_tVOC = air_ts[2]
    d_tVOC = {"timestamp": l_time, "VOC": l_tVOC}
    data_tVOC = pd.DataFrame(d_tVOC)
    data_tVOC.loc[data_tVOC['VOC'] > 2200, 'VOC'] = 2200
    data_tVOC["timestamp"] = pd.to_datetime(data_tVOC["timestamp"])
    data_tVOC.set_index('timestamp', inplace=True)
    thresholds_tVOC = thresholds["tVOC"]["lines"]
    graph_tVOC = plot_timeseries(data_tVOC, ABBR_TVOC, UNITS_TVOC, zipcode,
                                 cur_time, thresholds_tVOC)

    # print ("------- co2 ------------")
    l_co2 = air_ts[3]
    d_co2 = {"timestamp": l_time, "CO2": l_co2}
    data_co2 = pd.DataFrame(d_co2)
    print("DEBUG THIS MORNING")
    # df.loc[df['c1'] == 'Value', 'c2'] = 10
    data_co2.loc[data_co2['CO2'] > 5500, 'CO2'] = 5500
    print("DEBUG THIS MORNING")
    data_co2["timestamp"] = pd.to_datetime(data_co2["timestamp"])
    data_co2.set_index('timestamp', inplace=True)
    thresholds_co2 = thresholds["co2"]["lines"]
    graph_co2 = plot_timeseries(data_co2, ABBR_CO2, UNITS_CO2, zipcode,
                                cur_time, thresholds_co2)

    # print ("------- o3 ------------")
    l_o3 = air_ts[4]
    d_o3 = {"timestamp": l_time, "O3": l_o3}
    data_o3 = pd.DataFrame(d_o3)
    data_o3["timestamp"] = pd.to_datetime(data_o3["timestamp"])
    data_o3.set_index('timestamp', inplace=True)
    thresholds_o3 = thresholds["o3"]["lines"]
    graph_o3 = plot_timeseries(data_o3, ABBR_O3, UNITS_O3, zipcode, cur_time,
                               thresholds_o3)

    # print ("------- temp ------------")
    l_temp = air_ts[5]
    d_temp = {"timestamp": l_time, "Temperature": l_temp}
    data_temp = pd.DataFrame(d_temp)
    data_temp["timestamp"] = pd.to_datetime(data_temp["timestamp"])
    data_temp.set_index('timestamp', inplace=True)
    thresholds_temp = thresholds["temp"]["lines"]
    graph_temp = plot_timeseries(data_temp, ABBR_TEMP, UNITS_TEMP, zipcode,
                                 cur_time, thresholds_temp)

    # print ("------- hum ------------")
    l_hum = air_ts[6]
    d_hum = {"timestamp": l_time, "Humidity": l_hum}
    data_hum = pd.DataFrame(d_hum)
    data_hum["timestamp"] = pd.to_datetime(data_hum["timestamp"])
    data_hum.set_index('timestamp', inplace=True)
    thresholds_hum = thresholds["humidity"]["lines"]
    graph_hum = plot_timeseries(data_hum, ABBR_HUMIDITY, UNITS_HUMIDITY,
                                zipcode, cur_time, thresholds_hum)

    t2 = time.time()
    print("^^^^^^^^^^ DATA READINESS ^^^^^^^^^")
    print(t2 - t1)
    print("^^^^^^^^^^ END DATA READINESS ^^^^^^^^^")

    data = {
        "ts_pm25": graph_pm25,
        "ts_tVOC": graph_tVOC,
        "ts_co2": graph_co2,
        "ts_o3": graph_o3,
        "ts_temp": graph_temp,
        "ts_humidity": graph_hum
    }

    return data

