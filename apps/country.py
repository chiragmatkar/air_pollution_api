from flask import Blueprint, render_template

country = Blueprint("country",__name__,static_folder="static",template_folder="templates")



@country.route('/api/air/country/<country>', methods=['GET'])
def data_by_country(country):
    if request.method == 'GET':
        airs = Air.query.filter(Air.country == country).all()
        air_schema = AirSchema(many=True)
        output = air_schema.dump(airs).data
        return jsonify({'airs': output}), 200


@country.route('/api/air/country/<country>/state/<state>', methods=['GET'])
def data_by_country_state(country, state):
    if request.method == 'GET':
        airs = Air.query.filter(Air.country == country).filter(Air.state == state).all()
        air_schema = AirSchema(many=True)
        output = air_schema.dump(airs).data
        return jsonify({'airs': output}), 200


@country.route('/api/air/country/<country>/state/<state>/city/<city>', methods=['GET'])
def data_by_country_state_city(country, state, city):
    if request.method == 'GET':
        airs = Air.query.filter(Air.country == country).filter(Air.state == state).filter(Air.city == city).all()
        air_schema = AirSchema(many=True)
        output = air_schema.dump(airs).data
        return jsonify({'airs': output}), 200
