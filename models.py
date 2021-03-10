from datetime import datetime
from config import db, ma
from marshmallow import fields
from sqlalchemy import Index

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from config import app, db

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


class Air(db.Model):
    __tablename__ = 'air'
    air_id = db.Column(db.Integer, 
                          primary_key=True)
    timestamp = db.Column(db.DateTime, 
                          default=datetime.utcnow, 
                          onupdate=datetime.utcnow,
                          index=True)
    #Geographic
    city = db.Column(db.String)
    state = db.Column(db.String)
    country = db.Column(db.String)
    zipcode = db.Column(db.String, index=True)
    place = db.Column(db.String)
    details = db.Column(db.String)
    misc = db.Column(db.String)
    # Environmental
    tVOC = db.Column(db.Float)
    eCO2 = db.Column(db.Float)
    temp = db.Column(db.Float)
    pressure = db.Column(db.Float)
    altitude = db.Column(db.Float)
    humidity = db.Column(db.Float)
    # MQ2
    mq2_raw = db.Column(db.Float)
    mq2_ro = db.Column(db.Float)
    mq2_rs_by_ro = db.Column(db.Float)
    mq2_lpg_ppm = db.Column(db.Float)
    mq2_co_ppm = db.Column(db.Float)
    mq2_smoke_ppm = db.Column(db.Float)
    mq2_ref_ro = db.Column(db.Float)
    mq2_ref_lpg_ppm = db.Column(db.Float)
    mq2_ref_co_ppm = db.Column(db.Float)
    mq2_ref_smoke_ppm = db.Column(db.Float)
    # MQ4 - Natural gas
    mq4_raw = db.Column(db.Float)
    mq4_ro = db.Column(db.Float)
    mq4_rs_by_ro = db.Column(db.Float)
    mq4_ng_ppm = db.Column(db.Float)
    mq4_ng_ppm2 = db.Column(db.Float)
    mq4_ref_ro = db.Column(db.Float)
    mq4_ref_ng_ppm = db.Column(db.Float)
    # MQ6 - LPG
    mq6_raw = db.Column(db.Float)
    mq6_ro = db.Column(db.Float)
    mq6_rs_by_ro = db.Column(db.Float)
    mq6_lpg_ppm = db.Column(db.Float)
    mq6_lpg_ppm2 = db.Column(db.Float)
    mq6_ref_ro = db.Column(db.Float)
    mq6_ref_lpg_ppm = db.Column(db.Float)
    # MQ7 - CO
    mq7_raw = db.Column(db.Float)
    mq7_ro = db.Column(db.Float)
    mq7_rs_by_ro = db.Column(db.Float)
    mq7_co_ppm = db.Column(db.Float)
    mq7_h2_ppm = db.Column(db.Float)
    mq7_co_ppm2 = db.Column(db.Float)
    mq7_ref_ro = db.Column(db.Float)
    mq7_ref_co_ppm = db.Column(db.Float)
    mq7_ref_h2_ppm = db.Column(db.Float)
    # MQ131 - Ozone
    mq131_raw = db.Column(db.Float)
    mq131_ro = db.Column(db.Float)
    mq131_rs_by_ro = db.Column(db.Float)
    mq131_o3_ppm = db.Column(db.Float)
    mq131_o3_ppm2 = db.Column(db.Float)
    mq131_ref_ro = db.Column(db.Float)
    mq131_ref_o3_ppm = db.Column(db.Float)
    # CO2 sensor
    co2_raw = db.Column(db.Float)
    co2_ppm = db.Column(db.Float)
    # PM 2.5/dust sensor
    dust_raw = db.Column(db.Float)
    dust_Vo = db.Column(db.Float)
    dust_Voc = db.Column(db.Float)
    dust_dV = db.Column(db.Float)
    dust_Vo_mV = db.Column(db.Float)
    dustDensity = db.Column(db.Float)
    __table_args__ = (Index('zip_time_index', "zipcode", "timestamp"), )

#Index('zip_time_index', Air.zipcode, Air.timestamp)
Index('time_zip_index', Air.timestamp, Air.zipcode)

#class AirSchema(ma.ModelSchema):
class AirSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Air
        #sqla_session = db.session


if __name__ == '__main__':
    manager.run()
    # https://qxf2.com/blog/database-migration-flask-migrate/
    # https://www.bing.com/videos/search?q=I+added+index+to+my+models.py+file+in+flask.+How+do+I+migrate+the+data%3f&docid=608004190587324426&mid=E91E460768C1ADDA38FAE91E460768C1ADDA38FA&view=detail&FORM=VIREHT

