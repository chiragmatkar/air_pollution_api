from flask import Blueprint, jsonify, request, render_template
from models import Air, AirSchema
from config import app
date = Blueprint("date",__name__,static_folder="static",template_folder="templates")


def parse_date(date_str):
    yyyy_mm_dd = date_str.split('-')
    yyyy = int(yyyy_mm_dd[0])
    mm = int(yyyy_mm_dd[1])
    dd = int(yyyy_mm_dd[2])
    date_obj = date(year=yyyy,month=mm,day=dd)

    return date_obj


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