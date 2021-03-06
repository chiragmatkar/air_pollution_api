from flask import Flask
from apps import air_route ,atmosome,country,date_air,download,graph,timeseries_csv,zipcode
import matplotlib
print("Switched to:", matplotlib.get_backend())


print("P1")
# ----------
# app = connexion.FlaskApp(__name__, specification_dir='./')  # or e.g. Flask(__name__, template_folder='../otherdir')

app = Flask(__name__)
app.register_blueprint(air_route.air)
app.register_blueprint(atmosome.atmosome)
app.register_blueprint(country.country)
app.register_blueprint(date_air.date)
app.register_blueprint(download.download)
app.register_blueprint(graph.graph)
app.register_blueprint(timeseries_csv.timeseries_csv)
app.register_blueprint(zipcode.zipcode)

# Talisman(app)

# Read the swagger.yml file to configure the endpoints
# app.add_api('air.yml')


'''
@app.before_request
def before_request():
    scheme = request.headers.get('X-Forwarded-Proto')
    if scheme and scheme == 'http' and request.url.startswith('http://'):
        url = request.url.replace('http://', 'https://', 1)
        code = 301
        return redirect(url, code=code)
'''


@app.route('/', methods=['GET'])
def hello_world():
    print("I DID MAKE IT HERE")
    return '<h1>This is the Air Monitoring REST API site!!!</h1>', 200


if __name__== '__main__':
    app.run(host="0.0.0.0", port=8080)
