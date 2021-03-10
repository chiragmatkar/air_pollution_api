from flask import Blueprint, send_from_directory ,jsonify , abort
from config import app
from functions.graph_functions import hourly_data,cumulative_exposure_data,timeseries_data

atmosome = Blueprint("atmosome",__name__,static_folder="static",template_folder="templates")


@atmosome.route('/api/air/zipcode/<zipcode>/atmosome/summary', methods=['GET'])
def atmosome_data_summary(zipcode):
    data = hourly_data(zipcode)
    # data = hourly_data(zipcode, 720)s
    return jsonify(data), 200


@atmosome.route('/api/air/zipcode/<zipcode>/atmosome/cumulative', methods=['GET'])
def atmosome_data_cumulative(zipcode):
    data = cumulative_exposure_data(zipcode)

    return jsonify(data), 200


@atmosome.route('/api/air/zipcode/<zipcode>/atmosome/timeseries', methods=['GET'])
def atmosome_data_timeseries(zipcode):
    data = timeseries_data(zipcode)

    return jsonify(data), 200


@atmosome.route('/api/air/atmosome/html/<parameter>', methods=['GET'])
def read_html_static_page(parameter):
    filename = "{}/{}.html".format(app.config["CLIENT_TEMPLATES"], parameter)
    with open(filename, 'r') as f:
        content = f.read()
        data = {
            "content": content
        }

    return jsonify(data), 200


@atmosome.route('/api/air/zipcode/<zipcode>/atmosome', methods=['GET'])
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



@atmosome.route('/api/air/zipcode/<zipcode>/atmosome/timeseries/<filename>', methods=['GET'])
def data_by_graph_file(zipcode, filename):
    print ("------- I am in data_by_graph_file -------")
    try:
        return send_from_directory(app.config["CLIENT_GRAPHS"],
                                   filename=filename,
                                   as_attachment=True)
    except FileNotFoundError:
        abort(404)
