from flask import Blueprint, render_template
from config import app
from flask import send_file, send_from_directory, safe_join, abort
download = Blueprint("download",__name__,static_folder="static",template_folder="templates")

@download.route('/api/air/zipcode/<zipcode>/stanford/download', methods=['GET'])
def data_by_zipcode_download_csv(zipcode):
    if request.method == 'GET':
        airs = Air.query.filter(Air.zipcode == zipcode).all()
        # air_schema = AirSchema(many=True)
        # output = air_schema.dump(airs)
        # output = air_schema.dump(airs)
        print(airs[0])
        print(airs[0].mq2_raw)

        print("JEEEEEEEEEEEEESSSSSSSSSSSIIIIII")

        num_of_records = len(airs)
        print(num_of_records)
        raws = [air.mq2_raw for air in airs]
        ppms = [air.mq2_smoke_ppm for air in airs]

        data = {"raws": raws, "ppms": ppms}
        return jsonify({'data': data}), 200

        fname = datetime.utcnow()
        csv_fname = "{}_{}.csv".format(fname, zipcode)
        csv_fname = csv_fname.replace(" ", "_")
        csv_file_with_dir_name = "{}/{}".format(app.config["CLIENT_CSVS"], csv_fname)
        print("*********************** GB *************")
        print(csv_fname)
        print(csv_file_with_dir_name)
        print("*********************** GB *************")
        csv_columns = ["air_id", "timestamp", "city", "state", "country", "zipcode", "place", "details", "misc", "tVOC",
                       "eCO2", "temp", "pressure", "altitude", "humidity", "mq2_smoke_ppm", "mq4_ng_ppm", "mq6_lpg_ppm",
                       "mq7_co_ppm", "mq131_o3_ppm", "co2_ppm", "dustDensity"]

        with open(csv_file_with_dir_name, 'a+') as outfile:
            wr = csv.DictWriter(outfile, fieldnames=csv_columns, dialect='excel')
            wr.writeheader()
            for record in airs:
                wr.writerow(record)

        current_url = request.url
        urls = current_url.split("zipcode")
        parent_url = urls[0]

        csv_url = "{}downloads/{}".format(parent_url, csv_fname)
        message = ("Your query for zipcode {} resulted in {} records. "
                   "Please download your data as a csv file pasting this url in the browser: "
                   "{}"
                   ).format(zipcode, num_of_records, csv_url)
        return jsonify({'airs': message}), 200




# https://atm-rest.com/api/air/zipcode/95014/timeseries/csv/downloads/2020-12-08_04:13:49.978951.csv
@download.route('/api/air/<zipcode>/timeseries/csv/downloads/<filename>', methods=['GET'])
def data_by_csv_file(filename):
    try:
        return send_from_directory(app.config["CLIENT_CSVS"],
                                   filename=filename,
                                   as_attachment=True)
    except FileNotFoundError:
        abort(404)
