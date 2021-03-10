from flask import Blueprint, render_template
from config import app
from flask import send_file, send_from_directory, safe_join, abort
date = Blueprint("date",__name__,static_folder="static",template_folder="templates")



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