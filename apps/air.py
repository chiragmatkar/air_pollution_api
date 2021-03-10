from flask import Blueprint ,request,jsonify ,send_from_directory , abort
from functions import calculate_on_ref_Ro
from vars import *
from models import Air, AirSchema
from functions.calculate_on_ref_Ro import create_datetime_obj
from config import db
import datetime
from config import app
import csv
import json


air = Blueprint("air",__name__,static_folder="static",template_folder="templates")


@air.route('/api/air', methods=['GET', 'POST'])
def data():
    if request.method == 'POST':
        print("HERE HERE HERE HERE")
        print("Inside data method in post")
        # print ("Will print data received")
        data_elements = request.get_json(force=True)
        print("<<<<<<<<>>>>>>>>>>>>>")
        print(data_elements)
        print("<<<<<<<<>>>>>>>>>>>>>")
        # print ("printed data received")
        # print ("\n")
        date_str = data_elements.get("date_time")

        mq2_raw = float(data_elements['mq2_raw'])
        mq2_ref_lpg_ppm = calculate_on_ref_Ro(mq2_raw,
                                              MQ2_RL,
                                              MQ2_Ref_Ro,
                                              MQ2_LPGCurve
                                              )
        # print ("mq2 LPG: old: 0 ppm new: {0:.4f} ppm".format(mq2_ref_lpg_ppm))

        mq2_ref_co_ppm = calculate_on_ref_Ro(mq2_raw,
                                             MQ2_RL,
                                             MQ2_Ref_Ro,
                                             MQ2_COCurve
                                             )
        # print ("mq2 CO: old: 0 ppm new: {0:.4f} ppm".format(mq2_ref_co_ppm))

        mq2_ref_smoke_ppm = calculate_on_ref_Ro(mq2_raw,
                                                MQ2_RL,
                                                MQ2_Ref_Ro,
                                                MQ2_SmokeCurve
                                                )
        # print ("mq2 SMOKE: old: 0 ppm new: {0:.4f} ppm".format(mq2_ref_smoke_ppm))

        mq4_raw = float(data_elements['mq4_raw'])
        mq4_ref_ng_ppm = calculate_on_ref_Ro(mq4_raw,
                                             MQ4_RL,
                                             MQ4_Ref_Ro,
                                             MQ4_MethaneCurve
                                             )
        # print ("mq4 NG: old: 0 ppm new: {0:.4f} ppm".format(mq4_ref_ng_ppm))

        mq6_raw = float(data_elements['mq6_raw'])
        mq6_ref_lpg_ppm = calculate_on_ref_Ro(mq6_raw,
                                              MQ6_RL,
                                              MQ6_Ref_Ro,
                                              MQ6_LPGCurve
                                              )
        # print ("mq6 LPG: old: 0 ppm new: {0:.4f} ppm".format(mq6_ref_lpg_ppm))

        mq7_raw = float(data_elements['mq7_raw'])
        mq7_ref_co_ppm = calculate_on_ref_Ro(mq7_raw,
                                             MQ7_RL,
                                             MQ7_Ref_Ro,
                                             MQ7_COCurve
                                             )
        # print ("mq7: old CO: 0 ppm new CO: {0:.4f} ppm".format(mq7_ref_co_ppm))

        mq7_ref_h2_ppm = calculate_on_ref_Ro(mq7_raw,
                                             MQ7_RL,
                                             MQ7_Ref_Ro,
                                             MQ7_H2Curve
                                             )
        # print ("mq7: old H2: 0 ppm new H2: {0:.4f} ppm".format(mq7_ref_h2_ppm))

        try:
            mq131_raw = float(data_elements['mq131'])
        except KeyError as e:
            mq131_raw = float(data_elements['mq131_raw'])

        mq131_ref_o3_ppm = calculate_on_ref_Ro(mq131_raw,
                                               MQ131_RL,
                                               MQ131_Ref_Ro,
                                               MQ131_O3Curve
                                               )
        # print ("mq131: old: 0 ppm new: {0:.4f} ppm".format(mq131_ref_o3_ppm))

        zipcode = data_elements['zipcode']
        altitude = float(data_elements['altitude'])
        temp = float(data_elements['temp'])
        mq4_ng_ppm = float(data_elements['mq4_ng_ppm'])

        if zipcode == '94720':
            if altitude < 150:
                altitude = 177.0
            elif altitude > 210:
                altitude = 177.0

            if mq4_ng_ppm > 100:
                mq4_ng_ppm = mq4_ng_ppm / 100
        elif zipcode == '95014':
            if altitude < 180:
                altitude = 236.0
            elif altitude > 250:
                altitude = 236.0
        elif zipcode == '95064':
            if altitude < 650:
                altitude = 763.0
            elif altitude > 850:
                altitude = 763.0
            temp = temp - 5
        elif zipcode == '96150':
            if altitude < 5500:
                altitude = 6263.0
            elif altitude > 6350:
                altitude = 6263.0
        elif zipcode == '94305':
            if altitude < 135:
                altitude = 141.0
            elif altitude > 155:
                altitude = 141.0

        # hari redo co2 for blau lab
        co2_raw = float(data_elements['co2_raw'])
        co2_ppm = float(data_elements['co2_ppm'])

        if zipcode == '94305':
            concentration = co2_raw * 8
            # concentration = concentration/1.5;

            if concentration < 0:
                print("Not adjusting co2ppm.")
            else:
                print("concentration: {}".format(concentration))

                if concentration > 600:
                    concentration = (concentration * 1.5) / 1.4
                elif concentration > 1000:
                    concentration = (concentration * 1.5) / 1.3

                co2_raw = co2_ppm
                co2_ppm = concentration

                print("co2_ppm: {}".format(co2_ppm))
                print("END HARI ADJUSTED BLAU LAB CO2 END")

        if date_str:
            T_idx = date_str.find("T")
            if T_idx >= 0:
                datetime_obj = create_datetime_obj(date_str, delimiter="T")
            else:
                datetime_obj = create_datetime_obj(date_str)

            # temp=float(data_elements['temp']),
            air = Air(
                timestamp=datetime_obj,
                city=data_elements['city'],
                state=data_elements['state'],
                country=data_elements['country'],
                # zipcode=data_elements['zipcode'],
                zipcode=zipcode,
                place=data_elements['place'],
                details=data_elements['details'],
                misc=data_elements['misc'],
                tVOC=float(data_elements['tVOC']),
                eCO2=float(data_elements['eCO2']),
                temp=temp,
                pressure=float(data_elements['pressure']),
                # altitude=float(data_elements['altitude']),
                altitude=altitude,
                humidity=float(data_elements['humidity']),
                mq2_raw=mq2_raw,
                mq2_ro=float(data_elements['mq2_ro']),
                mq2_rs_by_ro=float(data_elements['mq2_rs_by_ro']),
                mq2_lpg_ppm=float(data_elements['mq2_lpg_ppm']),
                mq2_co_ppm=float(data_elements['mq2_co_ppm']),
                mq2_smoke_ppm=float(data_elements['mq2_smoke_ppm']),
                mq2_ref_ro=MQ2_Ref_Ro,
                mq2_ref_lpg_ppm=mq2_ref_lpg_ppm,
                mq2_ref_co_ppm=mq2_ref_co_ppm,
                mq2_ref_smoke_ppm=mq2_ref_smoke_ppm,
                mq4_raw=mq4_raw,
                mq4_ro=float(data_elements['mq4_ro']),
                mq4_rs_by_ro=float(data_elements['mq4_rs_by_ro']),
                # mq4_ng_ppm=float(data_elements['mq4_ng_ppm']),
                mq4_ng_ppm=mq4_ng_ppm,
                mq4_ng_ppm2=float(data_elements['mq4_ng_ppm2']),
                mq4_ref_ro=MQ4_Ref_Ro,
                mq4_ref_ng_ppm=mq4_ref_ng_ppm,
                mq6_raw=mq6_raw,
                mq6_ro=float(data_elements['mq6_ro']),
                mq6_rs_by_ro=float(data_elements['mq6_rs_by_ro']),
                mq6_lpg_ppm=float(data_elements['mq6_lpg_ppm']),
                mq6_lpg_ppm2=float(data_elements['mq6_lpg_ppm2']),
                mq6_ref_ro=MQ6_Ref_Ro,
                mq6_ref_lpg_ppm=mq6_ref_lpg_ppm,
                mq7_raw=mq7_raw,
                mq7_ro=float(data_elements['mq7_ro']),
                mq7_rs_by_ro=float(data_elements['mq7_rs_by_ro']),
                mq7_co_ppm=float(data_elements['mq7_co_ppm']),
                mq7_h2_ppm=float(data_elements['mq7_h2_ppm']),
                mq7_co_ppm2=float(data_elements['mq7_co_ppm2']),
                mq7_ref_ro=MQ7_Ref_Ro,
                mq7_ref_co_ppm=mq7_ref_co_ppm,
                mq7_ref_h2_ppm=mq7_ref_h2_ppm,
                mq131_raw=mq131_raw,
                mq131_ro=float(data_elements['mq131_ro']),
                mq131_rs_by_ro=float(data_elements['mq131_rs_by_ro']),
                mq131_o3_ppm=float(data_elements['mq131_o3_ppm']),
                mq131_o3_ppm2=float(data_elements['mq131_o3_ppm2']),
                mq131_ref_ro=MQ131_Ref_Ro,
                mq131_ref_o3_ppm=mq131_ref_o3_ppm,
                # co2_raw=float(data_elements['co2_raw']),
                # co2_ppm=float(data_elements['co2_ppm']),
                co2_raw=co2_raw,
                co2_ppm=co2_ppm,
                dust_raw=float(data_elements['dust_raw']),
                dust_Vo=float(data_elements['dust_Vo']),
                dust_Voc=float(data_elements['dust_Voc']),
                dust_dV=float(data_elements['dust_dV']),
                dust_Vo_mV=float(data_elements['dust_Vo_mV']),
                dustDensity=float(data_elements['dustDensity']),
            )
        else:
            print("-------")
            print(data_elements['eCO2'])
            print("---------")
            air = Air(
                city=data_elements['city'],
                state=data_elements['state'],
                country=data_elements['country'],
                # zipcode=data_elements['zipcode'],
                zipcode=zipcode,
                place=data_elements['place'],
                details=data_elements['details'],
                misc=data_elements['misc'],
                tVOC=float(data_elements['tVOC']),
                eCO2=float(data_elements['eCO2']),
                # temp=float(data_elements['temp']),
                temp=temp,
                pressure=float(data_elements['pressure']),
                # altitude=float(data_elements['altitude']),
                altitude=altitude,
                humidity=float(data_elements['humidity']),
                mq2_raw=mq2_raw,
                mq2_ro=float(data_elements['mq2_ro']),
                mq2_rs_by_ro=float(data_elements['mq2_rs_by_ro']),
                mq2_lpg_ppm=float(data_elements['mq2_lpg_ppm']),
                mq2_co_ppm=float(data_elements['mq2_co_ppm']),
                mq2_smoke_ppm=float(data_elements['mq2_smoke_ppm']),
                mq2_ref_ro=MQ2_Ref_Ro,
                mq2_ref_lpg_ppm=mq2_ref_lpg_ppm,
                mq2_ref_co_ppm=mq2_ref_co_ppm,
                mq2_ref_smoke_ppm=mq2_ref_smoke_ppm,
                mq4_raw=mq4_raw,
                mq4_ro=float(data_elements['mq4_ro']),
                mq4_rs_by_ro=float(data_elements['mq4_rs_by_ro']),
                # mq4_ng_ppm=float(data_elements['mq4_ng_ppm']),
                mq4_ng_ppm=mq4_ng_ppm,
                mq4_ng_ppm2=float(data_elements['mq4_ng_ppm2']),
                mq4_ref_ro=MQ4_Ref_Ro,
                mq4_ref_ng_ppm=mq4_ref_ng_ppm,
                mq6_raw=mq6_raw,
                mq6_ro=float(data_elements['mq6_ro']),
                mq6_rs_by_ro=float(data_elements['mq6_rs_by_ro']),
                mq6_lpg_ppm=float(data_elements['mq6_lpg_ppm']),
                mq6_lpg_ppm2=float(data_elements['mq6_lpg_ppm2']),
                mq6_ref_ro=MQ6_Ref_Ro,
                mq6_ref_lpg_ppm=mq6_ref_lpg_ppm,
                mq7_raw=mq7_raw,
                mq7_ro=float(data_elements['mq7_ro']),
                mq7_rs_by_ro=float(data_elements['mq7_rs_by_ro']),
                mq7_co_ppm=float(data_elements['mq7_co_ppm']),
                mq7_h2_ppm=float(data_elements['mq7_h2_ppm']),
                mq7_co_ppm2=float(data_elements['mq7_co_ppm2']),
                mq7_ref_ro=MQ7_Ref_Ro,
                mq7_ref_co_ppm=mq7_ref_co_ppm,
                mq7_ref_h2_ppm=mq7_ref_h2_ppm,
                mq131_raw=mq131_raw,
                mq131_ro=float(data_elements['mq131_ro']),
                mq131_rs_by_ro=float(data_elements['mq131_rs_by_ro']),
                mq131_o3_ppm=float(data_elements['mq131_o3_ppm']),
                mq131_o3_ppm2=float(data_elements['mq131_o3_ppm2']),
                mq131_ref_ro=MQ131_Ref_Ro,
                mq131_ref_o3_ppm=mq131_ref_o3_ppm,
                # co2_raw=float(data_elements['co2_raw']),
                # co2_ppm=float(data_elements['co2_ppm']),
                co2_raw=co2_raw,
                co2_ppm=co2_ppm,
                dust_raw=float(data_elements['dust_raw']),
                dust_Vo=float(data_elements['dust_Vo']),
                dust_Voc=float(data_elements['dust_Voc']),
                dust_dV=float(data_elements['dust_dV']),
                dust_Vo_mV=float(data_elements['dust_Vo_mV']),
                dustDensity=float(data_elements['dustDensity']),
            )

        # try:
        db.session.add(air)
        db.session.commit()
        print("COMMIT WENT FINE")
        # except Exception as e:
        #    print (e)
        #    print ("OMG I HIT A STUPID EXCEPTION")
        # //sqlite3.OperationalError:
        #    time.sleep(random.randint(10, 30))
        # data, code = create(air)
        air_schema = AirSchema()
        print("-------------")
        print("-------------")
        print("-------------")
        print(air_schema)
        print("-------------")
        print(air_schema.dump(air))
        print("-------------")
        print("-------------")
        print("-------------")

        output = air_schema.dump(air).get("data")
        return jsonify({'air': output}), 201
    elif request.method == 'GET':
        print(request.url)
        fname = str(datetime.utcnow())
        fname = "{}.json".format(fname)
        print("*********************** GB *************")
        print(fname)
        print("*********************** GB *************")
        # return jsonify({'airs': fname}), 200

        # Create the list of air from our data
        airs = Air.query.order_by(Air.timestamp).all()

        air_schema = AirSchema(many=True)
        output = air_schema.dump(airs).data
        print(type(output))
        print(output[0])
        num_of_records = len(output)
        print(num_of_records)
        if (num_of_records > 100):
            fname = datetime.utcnow()
            json_fname = "{}.json".format(fname)
            json_fname = json_fname.replace(" ", "_")
            print("I AM HERE")
            print(json_fname)
            json_file_with_dir_name = "{}/{}".format(app.config["CLIENT_CSVS"], json_fname)
            print("*********************** GB *************")
            print(json_fname)
            print(json_file_with_dir_name)
            print("*********************** GB *************")

            csv_fname = "{}.csv".format(fname)
            csv_fname = csv_fname.replace(" ", "_")
            csv_file_with_dir_name = "{}/{}".format(app.config["CLIENT_CSVS"], csv_fname)
            print("*********************** GB *************")
            print(csv_fname)
            print(csv_file_with_dir_name)
            print("*********************** GB *************")
            csv_columns = ["air_id", "timestamp", "city", "state", "country", "zipcode", "place", "details", "misc",
                           "tVOC", "eCO2", "temp", "pressure", "altitude", "humidity", "mq2_smoke_ppm", "mq4_ng_ppm",
                           "mq6_lpg_ppm", "mq7_co_ppm", "mq131_o3_ppm", "co2_ppm", "dustDensity"]
            with open(csv_file_with_dir_name, 'a+') as outfile:
                wr = csv.DictWriter(outfile, fieldnames=csv_columns, dialect='excel')
                wr.writeheader()
                for record in output:
                    wr.writerow(record)

            with open(json_file_with_dir_name, 'a+') as outfile:
                outfile.write(json.dumps(output))
                outfile.write("\n")

            csv_url = "{}/downloads/{}".format(request.url, csv_fname)
            json_url = "{}/downloads/{}".format(request.url, json_fname)
            message = ("Your query resulted in {} records. "
                       "This is too much data to embed in this result. "
                       "Please download the json file pasting this url in the browser: "
                       "{}"
                       " Or, download the file in csv format by pasting this link in the browser: "
                       "{}"
                       ).format(num_of_records, json_url, csv_url)
            return jsonify({'airs': message}), 200
        else:
            return jsonify({'airs': output}), 200

        return jsonify({'airs': "Data has been saved on server"}), 200


@app.route('/api/air/downloads_deprecated/<filename>', methods=['GET'])
def data_by_json_file(filename):
    try:
        return send_from_directory(app.config["CLIENT_CSVS"],
                                   filename=filename,
                                   as_attachment=True)
    except FileNotFoundError:
        abort(404)