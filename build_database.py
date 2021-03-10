import os
from config import db
from models import Air

# Data to initialize database with

# Delete database file if it exists currently
if os.path.exists("air_lite_v4.db"):
    os.remove("air_lite_v4.db")

# Create the database
db.create_all()

# iterate over the data structure and populate the database

db.session.commit()

