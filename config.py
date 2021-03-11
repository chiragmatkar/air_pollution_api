import os
#import connexion
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask import Flask

basedir = os.path.abspath(os.path.dirname(__file__))


print ("----------------------")
print (basedir)
print ("---------------------")


# reate_engine('sqlite:///{}'.format(xxx), connect_args={'timeout': 15})

# Create the connexion application instance
#connex_app = connexion.App(__name__, specification_dir=basedir)

# Get the underlying Flask app instance
#app = connex_app.app
app = Flask(__name__)

CORS(app)
#Talisman(app)

# Build the Sqlite ULR for SqlAlchemy
#sqlite_url = "sqlite:////" + os.path.join(basedir, "air_lite_v3.db")
#sqlite_url = "sqlite:////" + os.path.join(basedir, "air_lite_v5.db")
sqlite_url = "postgres://ubuntu:ubuntu1234@localhost/air_post_v1"

# Configure the SqlAlchemy part of the app instance
app.config["SQLALCHEMY_ECHO"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = sqlite_url
#app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# The absolute path of the directory containing JSON files for users to download

# The absolute path of the directory containing user stuff
app.config["CLIENT_CONFIGS"] = "/home/ubuntu/flaskproject/configs"
app.config["CLIENT_TEMPLATES"] = "/home/ubuntu/flaskproject/templates"
app.config["CLIENT_GRAPHS"] = "/home/ubuntu/flaskproject/downloads/graphs"
app.config["CLIENT_CSVS"] = "/home/ubuntu/flaskproject/downloads/csvs"

# lock error resolution?
# app.db = SQLAlchemy(app, engine_options={"pool_pre_ping": True})

# Create the SqlAlchemy db instance
db = SQLAlchemy(app)

# Initialize Marshmallow
ma = Marshmallow(app)

