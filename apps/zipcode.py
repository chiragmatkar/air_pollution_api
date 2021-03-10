from flask import Blueprint, render_template , request , jsonify
from config import app
from flask import send_file, send_from_directory, safe_join, abort
from models import Air, AirSchema

zipcode = Blueprint("zipcode",__name__,static_folder="static",template_folder="templates")



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




@zipcode.route('/api/air/zipcode/<zipcode>/timeseries/graphs/smoke/<filename>', methods=['GET'])
def data_by_smoke_graph_file(zipcode, filename):
    try:
        return send_from_directory(app.config["CLIENT_GRAPHS"],
                                   filename=filename,
                                   as_attachment=True)
    except FileNotFoundError:
        abort(404)


@zipcode.route('/api/air/zipcode/<zipcode>/timeseries/graphs/ng/<filename>', methods=['GET'])
def data_by_ng_graph_file(zipcode, filename):
    try:
        return send_from_directory(app.config["CLIENT_GRAPHS"],
                                   filename=filename,
                                   as_attachment=True)
    except FileNotFoundError:
        abort(404)


@app.route('/api/air/zipcode/<zipcode>/timeseries/csv/days/<num_of_days>', methods=['GET'])
def csv_timeseries_num_days(zipcode, num_of_days):
    days = int(num_of_days)
    return csv_timeseries(zipcode, days)


@app.route('/api/air/zipcode/<zipcode>', methods=['GET'])
def data_by_zipcode(zipcode):
    if request.method == 'GET':
        airs = Air.query.filter(Air.zipcode == zipcode).all()
        air_schema = AirSchema(many=True)
        output = air_schema.dump(airs).data
        return jsonify({'airs': output}), 200
        return jsonify({'airs': output}), 200



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
