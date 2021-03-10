from flask import Blueprint, render_template , jsonify , request
from config import app
from datetime import date, datetime, timedelta
import time
import json
from flask import send_file, send_from_directory, safe_join, abort
from models import Air, AirSchema
from pandas import pd

timeseries_csv = Blueprint("timeseries_csv",__name__,static_folder="static",template_folder="templates")


@timeseries_csv.route('/api/air/zipcode/<zipcode>/timeseries/csv', methods=['GET'])
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


@timeseries_csv.route('/api/air/zipcode/<zipcode>/timeseries/csv/days/<num_of_days>', methods=['GET'])
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

