from models import Air, AirSchema
from datetime import date, datetime, timedelta

def timeseries_data(zipcode):
    graphs = timeseries_graphs(zipcode)

    if not graphs:
        ts_data = {
            "timeSeriesData": []
        }
        return ts_data

    data_pm25 = {
        "name": "PM2.5",
        "graphImageUrl": graphs["ts_pm25"],
        "order": 1
    }

    data_tVOC = {
        "name": "tVOC",
        "graphImageUrl": graphs["ts_tVOC"],
        "order": 2
    }

    data_co2 = {
        "name": "CO2",
        "graphImageUrl": graphs["ts_co2"],
        "order": 3
    }

    data_o3 = {
        "name": "O3",
        "graphImageUrl": graphs["ts_o3"],
        "order": 4
    }

    data_temp = {
        "name": "Temperature",
        "graphImageUrl": graphs["ts_temp"],
        "order": 5
    }

    data_hum = {
        "name": "Humidity",
        "graphImageUrl": graphs["ts_humidity"],
        "order": 6
    }

    ts_data = {
        "timeSeriesData": [data_pm25, data_tVOC, data_co2, data_o3,
                           data_temp, data_hum]
    }

    # print (ts_data)
    return ts_data


def ORIGINAL_SUMMARY_cumulative_data(zipcode, num_of_days):
    past_time = datetime.now() - timedelta(days=num_of_days)

    # t1 = time.time()
    airdata = Air.query.with_entities(
        func.sum(Air.dustDensity).label('avg_pm25'),
        func.sum(Air.tVOC).label('avg_tVOC'),
        func.sum(Air.co2_ppm).label('avg_co2'),
        func.sum(Air.mq131_o3_ppm).label('avg_o3')
    ).filter(Air.zipcode == zipcode, Air.timestamp >= past_time).all()

    # t2 = time.time()
    if not airdata:
        return {}

    air_aggrs = airdata[0]

    # t3 = time.time()
    data = {
        "total_pm25": air_aggrs[0],
        "total_tVOC": air_aggrs[1],
        "total_co2": air_aggrs[2],
        "total_o3": air_aggrs[3]
    }
    # print (data)
    return data


def cumulative_data(zipcode, num_of_hours):
    past_time = datetime.now() - timedelta(hours=num_of_hours)

    # t1 = time.time()
    airdata = Air.query.with_entities(
        func.avg(Air.dustDensity).label('avg_pm25'),
        func.avg(Air.tVOC).label('avg_tVOC'),
        func.avg(Air.co2_ppm).label('avg_co2'),
        func.avg(Air.mq131_o3_ppm).label('avg_o3')
    ).filter(Air.zipcode == zipcode, Air.timestamp >= past_time).all()

    # t2 = time.time()
    if not airdata:
        data = {
            "avg_pm25": "N/A",
            "avg_tVOC": "N/A",
            "avg_co2": "N/A",
            "avg_o3": "N/A"
        }
        return data

    air_aggrs = airdata[0]

    if not air_aggrs:
        data = {
            "avg_pm25": "N/A",
            "avg_tVOC": "N/A",
            "avg_co2": "N/A",
            "avg_o3": "N/A"
        }
        return data
    else:
        if air_aggrs[0]:
            val_pm25 = round(air_aggrs[0], 2)
        else:
            val_pm25 = "N/A"

        if air_aggrs[1]:
            val_tVOC = round(air_aggrs[1], 2)
        else:
            val_tVOC = "N/A"

        if air_aggrs[2]:
            val_co2 = round(air_aggrs[2], 2)
        else:
            val_co2 = "N/A"

        if air_aggrs[3]:
            val_o3 = round(air_aggrs[3], 2)
        else:
            val_o3 = "N/A"

    # t3 = time.time()
    data = {
        "avg_pm25": val_pm25,
        "avg_tVOC": val_tVOC,
        "avg_co2": val_co2,
        "avg_o3": val_o3
    }
    # print (data)
    return data


def cumulative_exposure_data(zipcode):
    # past_8_hours = cumulative_data(zipcode, 22)
    past_8_hours = cumulative_data(zipcode, 8)
    past_24_hours = cumulative_data(zipcode, 24)
    past_week = cumulative_data(zipcode, 168)

    data_pm25 = {
        "name": ABBR_PM25,
        "unit": UNITS_PM25,
        "order": 1,
        "stats": [
            {
                "title": "8 Hours",
                "order": 1,
                "stats": past_8_hours["avg_pm25"]
            },
            {
                "title": "24 Hours",
                "order": 2,
                "stats": past_24_hours["avg_pm25"]
            },
            {
                "title": "1 week",
                "order": 3,
                "stats": past_week["avg_pm25"]
            }
        ]
    }

    data_tVOC = {
        "name": ABBR_TVOC,
        "unit": UNITS_TVOC,
        "order": 2,
        "stats": [
            {
                "title": "8 Hours",
                "order": 1,
                "stats": past_8_hours["avg_tVOC"]
            },
            {
                "title": "24 Hours",
                "order": 2,
                "stats": past_24_hours["avg_tVOC"]
            },
            {
                "title": "1 week",
                "order": 3,
                "stats": past_week["avg_tVOC"]
            }
        ]
    }

    data_co2 = {
        "name": ABBR_CO2,
        "unit": UNITS_CO2,
        "order": 3,
        "stats": [
            {
                "title": "8 Hours",
                "order": 1,
                "stats": past_8_hours["avg_co2"]
            },
            {
                "title": "24 Hours",
                "order": 2,
                "stats": past_24_hours["avg_co2"]
            },
            {
                "title": "1 week",
                "order": 3,
                "stats": past_week["avg_co2"]
            }
        ]
    }

    data_o3 = {
        "name": ABBR_O3,
        "unit": UNITS_O3,
        "order": 4,
        "stats": [
            {
                "title": "8 Hours",
                "order": 1,
                "stats": past_8_hours["avg_o3"]
            },
            {
                "title": "24 Hours",
                "order": 2,
                "stats": past_24_hours["avg_o3"]
            },
            {
                "title": "1 week",
                "order": 3,
                "stats": past_week["avg_o3"]
            }
        ]
    }

    average_exposure = {
        "averageExposure": [data_pm25, data_tVOC, data_co2, data_o3]
    }

    return average_exposure


def calculate_ugm3(weight, ppb):
    return (ppb * (weight / 22.41))


def hourly_data(zipcode, num_of_hours=ONE_HOUR):
    pollutants_vals = ["N/A"] * NUM_OF_POLLLUTANTS
    pollutants_units = [""] * NUM_OF_POLLLUTANTS
    bar_vals = [0] * NUM_OF_POLLLUTANTS
    bar_colors = ["GREEN"] * NUM_OF_POLLLUTANTS
    pollutants_states = ["N/A"] * NUM_OF_POLLLUTANTS
    weather_vals = ["N/A"] * 4
    weather_units = [""] * 4
    aqi_val = 0

    POLLUTANTS_DATA_AVAILABLE = True
    WEATHER_DATA_AVAILABLE = True

    past_time = datetime.now() - timedelta(hours=num_of_hours)

    airdata = Air.query.with_entities(
        func.avg(Air.dustDensity).label('avg_pm25'),
        func.avg(Air.tVOC).label('avg_tVOC'),
        func.avg(Air.co2_ppm).label('avg_co2'),
        func.avg(Air.mq131_o3_ppm).label('avg_o3'),
        func.avg(Air.mq7_co_ppm).label('avg_co'),
        func.avg(Air.mq2_smoke_ppm).label('avg_smoke'),
        func.avg(Air.mq6_lpg_ppm).label('avg_lpg'),
        func.avg(Air.mq4_ng_ppm).label('avg_ng'),
        func.avg(Air.eCO2).label('avg_eCO2'),
        func.avg(Air.mq7_h2_ppm).label('avg_h2'),
        func.avg(Air.temp).label('avg_temp'),
        func.avg(Air.humidity).label('avg_humidity'),
        func.avg(Air.pressure).label('avg_pressure'),
        func.avg(Air.altitude).label('avg_altitude')
    ).filter(Air.zipcode == zipcode, Air.timestamp >= past_time).all()

    print(airdata)
    print("^^^^^^^^^^^^^^^^^^")

    air_avgs = airdata[0]

    total_nones = air_avgs.count(None)
    if total_nones == 14:
        POLLUTANTS_DATA_AVAILABLE = False
        WEATHER_DATA_AVAILABLE = False
    else:
        pollut_nones = air_avgs[:10].count(None)
        weather_nones = air_avgs[10:].count(None)

        if pollut_nones == 10:
            POLLUTANTS_DATA_AVAILABLE = False
        if weather_nones == 4:
            WEATHER_DATA_AVAILABLE = False

    # POLLUTANT ORDER in the arrays
    # PM25, TVOC, CO2, O3, CO, SMOKE, LPG, NG, eCO2, H2, TEMP, HUMIDITY, PRESSURE, ALTITUDE]
    '''
        [Tue Sep 29 17:13:48.301222 2020] [wsgi:error] [pid 30589:tid 139834142594816] [remote 69.110.136.169:50574] %%%%%%%% BEGIN AVERAGES 
        [Tue Sep 29 17:13:48.301238 2020] PM2.5      14.3315846994536
        [Tue Sep 29 17:13:48.301249 2020] TVOC       29.6338797814208
        [Tue Sep 29 17:13:48.301260 2020] CO2        1565.87978142077
        [Tue Sep 29 17:13:48.301271 2020] O3         0.0278196721311475
        [Tue Sep 29 17:13:48.301284 2020] CO         0.632240437158469
        [Tue Sep 29 17:13:48.301295 2020] SMOKE      364.229508196721
        [Tue Sep 29 17:13:48.301307 2020] LPG        1.28360655737705
        [Tue Sep 29 17:13:48.301319 2020] NG         1.56224043715847
        [Tue Sep 29 17:13:48.301331 2020] eCO2       597.622950819672
        [Tue Sep 29 17:13:48.301341 2020] H2         0.0
        [Tue Sep 29 17:13:48.301353 2020] TEMP       19.2928961748634
        [Tue Sep 29 17:13:48.301364 2020] HUMIDITY   58.0546448087432
        [Tue Sep 29 17:13:48.301376 2020] PRESSURE   100455.65852459
        [Tue Sep 29 17:13:48.301387 2020] ALTITUDE   72.6219672131148
        '''

    if WEATHER_DATA_AVAILABLE:
        # altitude adjustment
        '''
                val = air_avgs[13]
                if zipcode == '94720':
                    if  val < 150:
                        val = 177.0
                elif zipcode == '95014':
                    if  val < 180:
                        val = 236.0
                elif zipcode == '96150':
                    if  val < 5500:
                        val = 6263.0
                '''

        val = air_avgs[13]
        if zipcode == '94720':
            if val < 150:
                val = 177.0
            elif val > 210:
                val = 177.0
        elif zipcode == '95014':
            if val < 180:
                val = 236.0
            elif val > 250:
                val = 236.0
        elif zipcode == '95064':
            if val < 650:
                val = 763.0
            elif val > 850:
                val = 763.0
        elif zipcode == '96150':
            if val < 5500:
                val = 6263.0
            elif val > 6350:
                val = 6263.0
        elif zipcode == '94305':
            if val < 135:
                val = 141.0
            elif val > 155:
                val = 141.0

        '''
                if air_avgs[13] < 30:
                    val = air_avgs[13] * 5
                else:
                    val = air_avgs[13]
                    if val < 80:
                        val = 115
                '''
        weather_vals = [air_avgs[10], air_avgs[11], air_avgs[12], val]
        # weather_vals = [air_avgs[10], air_avgs[11], air_avgs[12], air_avgs[13]]
        weather_units = WEATHER_UNITS

    if POLLUTANTS_DATA_AVAILABLE:
        lpgval = air_avgs[6]
        while lpgval > 10:
            lpgval = lpgval / 10

        ng_val = air_avgs[7]

        co_val = air_avgs[4] / 10
        smoke_val = air_avgs[5] / 10
        # while ng_val > 10:
        #    ng_val = ng_val/10

        pollutants_vals = [air_avgs[0], air_avgs[1], air_avgs[2], air_avgs[3],
                           co_val, smoke_val, lpgval, ng_val,
                           air_avgs[8], air_avgs[9]]

        ''' ORG
                pollutants_vals = [air_avgs[0], air_avgs[1], air_avgs[2], air_avgs[3],
                                    air_avgs[4], air_avgs[5], lpgval, ng_val,
                                    air_avgs[8], air_avgs[9]]
                '''

        '''
                pollutants_vals = [air_avgs[0], air_avgs[1], air_avgs[2], air_avgs[3],
                                    air_avgs[4], air_avgs[5], air_avgs[6], air_avgs[7],
                                    air_avgs[8], air_avgs[9]]
                '''
        '''
                PM2.5 - 1.248920438
                PM10 - 0.740816327
                SO2 - 0.400181718
                O3 - 0.429166667
                CO - 5.37414966
                NO2 - 0.252687954
                '''

        print(air_avgs)
        print("------- vals --------")
        # PM25, tVOC, CO2, O3, CO
        # (21.4408333333333,
        # 7.92857142857143,
        # 459.70630952381,
        # 0.0611547619047619,
        # 8.01428571428571,
        # 4444.63095238095, 0.0, 5.9522619047619, 455.154761904762, 0.0, 84.4035714285714, 44.0238095238095, 29.7013095238095, 203.990238095238)

        # [(19.7606666666667, 240.083333333333, 1528.04866666667, 0.03175, 4.23333333333333, 0.0, 0.0, 2.7565, 1559.23333333333, 0.0, 77.8516666666667, 38.2166666666667, 29.682, 220.803833333333)]

        # aqi_val = air_avgs[0]*1.248920438 + air_avgs[1]*0.740816327 + air_avgs[2]*0.400181718 + air_avgs[3]*0.429166667 + air_avgs[4]*5.37414966
        # aqi_val = air_avgs[0]*1.248920438 + air_avgs[1]*0.740816327 + air_avgs[3]*0.429166667 + air_avgs[4]*5.37414966

        '''
                Nitrogen dioxide 1 ppb = 1.91 ug/m3
                Sulphur dioxide 1 ppb = 2.66 ug/m3
                Ozone 1 ppb = 2.0 ug/m3
                Carbon monoxide 1 ppb = 1.16 ug/m3
                Benzene 1 ppb = 3.24 ug/m3

                SO2 - 0.400181718
                NO2 - 0.252687954
                PM10 - 0.740816327
                O3 - 0.429166667
                PM2.5 - 1.248920438
                CO - 0.00537414966
                '''
        '''

                #0.0409 x concentration (ppm) x molecular weigh
                # https://www.teesing.com/en/page/library/tools/ppm-mg3-converter
                0.0409 * <ppm> * <mol_weight>
                # PM25, tVOC, CO2, O3, CO, Smoke, LPG, NG, eCO2, H2
                tvoc_ug_m3 = 0.0409 * 78.9516 * air_avgs[1]
                co2_ug_m3 = 0.0409 * 44.01 * air_avgs[2]


                caluclate_ugm3
                if (counter == NO2)
                   # no2 values produced are already in ppb
                   ugm3_no2 = 	caluclate_ugm3(46.01, no2_counter_value)
                elif (counter == SO2)
                   # so2 values produced are already in ppb
                   ugm3_so2 = 	caluclate_ugm3(64.06, so2_counter_value)
                        elif (counter == O3)   
                   # O3 values produced are already in ppm in atomosme
                   ugm3_o3 = 	caluclate_ugm3(48.00, O3_counter_value/1000)
                elif (counter == CO)   
                   # CO values produced are already in ppm
                   ugm3_co = caluclate_ugm3(28.01, co_counter_value/1000)  
               '''

        # air_avgs[1] = 1549.83
        # air_avgs[3] = 0.12

        # Replacing no2 with co2
        # Replacing so2 with tVOC
        ugm3_pm25 = air_avgs[0]
        # ugm3_tvoc = calculate_ugm3(78.9516, air_avgs[1])
        ugm3_tvoc = calculate_ugm3(60.9516, air_avgs[1])
        ugm3_co2 = calculate_ugm3(44.01, air_avgs[2])
        ugm3_o3 = calculate_ugm3(48.00, air_avgs[3])
        ugm3_o3 = calculate_ugm3(48.00, air_avgs[3])
        # ugm3_co = calculate_ugm3(28.01, air_avgs[4])
        ugm3_co = calculate_ugm3(28.01, co_val)
        # ugm3_pm10 = air_avgs[5]
        ugm3_pm10 = smoke_val

        # final_aqi = (ugm3_co2 * 0.252687954) + (ugm3_tvoc * 0.400181718) + (ugm3_o3 * 0.429166667) + (ugm3_co * 0.00537414966) + (ugm3_pm25 * 1.248920438) + (ugm3_pm10 * 0.740816327)
        # final_aqi = (ugm3_co2 * 0.002526) + (ugm3_tvoc * 0.400181718) + (ugm3_o3 * 0.429166667) + (ugm3_co * 0.00537414966) + (ugm3_pm25 * 1.248920438) + (ugm3_pm10 * 0.740816327)
        final_aqi = (ugm3_co2 * 0.252687954 / 100) + (ugm3_tvoc * 0.400181718 / 10) + (ugm3_o3 * 0.429166667) + (
                ugm3_co * 0.00537414966) + (ugm3_pm25 * 1.248920438) + (ugm3_pm10 * 0.740816327 / 100.0)

        ######aqi_val = air_avgs[0]*1.248920438 + air_avgs[3]*0.429166667 + air_avgs[4]*5.37414966
        # aqi_val = air_avgs[0]*1.248920438 + air_avgs[1]*0.740816327 + air_avgs[2]*0.400181718 + air_avgs[3]*0.429166667
        aqi_val = final_aqi
        aqi_val = round(aqi_val)
        pollutants_units = POLLUTANTS_UNITS
        pollutants_states = []
        bar_colors = []
        bar_vals = []

        # PM2.5
        state, color = get_PM25_state_barColor(pollutants_vals[0])
        pollutants_states.append(state)
        bar_colors.append(color)
        val = get_barValue(air_avgs[0], PM25_max)
        bar_vals.append(val)

        # TVOC
        state, color = get_VOC_state_barColor(air_avgs[1])
        pollutants_states.append(state)
        bar_colors.append(color)
        val = get_barValue(air_avgs[1], tVOC_max)
        bar_vals.append(val)

        # CO2
        state, color = get_CO2_state_barColor(air_avgs[2])
        pollutants_states.append(state)
        bar_colors.append(color)
        val = get_barValue(air_avgs[2], CO2_max)
        bar_vals.append(val)

        # O3
        state, color = get_O3_state_barColor(air_avgs[3])
        pollutants_states.append(state)
        bar_colors.append(color)
        val = get_barValue(air_avgs[3], O3_max)
        bar_vals.append(val)

        # CO
        # state, color = get_CO_state_barColor(air_avgs[4])
        state, color = get_CO_state_barColor(co_val)
        pollutants_states.append(state)
        bar_colors.append(color)
        # val =  get_barValue(air_avgs[4], CO_max)
        val = get_barValue(co_val, CO_max)
        bar_vals.append(val)

        # Smoke
        # state, color = get_Smoke_state_barColor(air_avgs[5])
        state, color = get_Smoke_state_barColor(smoke_val)
        pollutants_states.append(state)
        bar_colors.append(color)
        # val =  get_barValue(air_avgs[5], Smoke_max)
        val = get_barValue(smoke_val, Smoke_max)
        bar_vals.append(val)

        # LPG
        state, color = get_LPG_state_barColor(air_avgs[6])
        pollutants_states.append(state)
        bar_colors.append(color)
        val = get_barValue(air_avgs[6], LPG_max)
        bar_vals.append(val)

        # NG
        # state, color = get_NG_state_barColor(air_avgs[7])
        state, color = get_NG_state_barColor(ng_val)
        pollutants_states.append(state)
        bar_colors.append(color)

        # GAYATRI
        # air_avgs[7] = 10
        val = get_barValue(ng_val, NG_max)
        bar_vals.append(val)

        # eCO2
        state, color = get_eCO2_state_barColor(air_avgs[8])
        pollutants_states.append(state)
        bar_colors.append(color)
        val = get_barValue(air_avgs[8], CO2_max)
        bar_vals.append(val)

        # H2
        state, color = get_H2_state_barColor(air_avgs[9])
        pollutants_states.append(state)
        bar_colors.append(color)
        # PUT H2 MAX
        val = get_barValue(air_avgs[9], CO_max)
        bar_vals.append(val)

    # t3 = time.time()

    '''
        print ("&&&&&&&&&&&&&&& DD average &&&&&&&&&&&&&&&&&&&&")
        print (t2-t1)
        print (type(airdata))
        print ("start data")
        print (airdata)
        print (t3-t2)
        print ("&&&&&&&&&&&&&&& END DD average &&&&&&&&&&&&&&&&&&&&")
        '''

    # t1 = time.time()
    geo = Air.query.with_entities(
        Air.city,
        Air.state,
        Air.country,
        Air.place
    ).filter(Air.zipcode == zipcode).first()

    if geo:
        location_data = {
            "zipCode": zipcode,
            "city": geo[0],
            "state": geo[1],
            "country": geo[2],
            "place": geo[3]
        }
    else:
        location_data = {
            "zipCode": zipcode,
            "city": "N/A",
            "state": "N/A",
            "country": "N/A",
            "place": "N/A"
        }
    # print ("$$$$$$$$$$$$$$$")
    # print (location_data)
    # print ("$$$$$$$$$$$$$$$")

    # "barColor": bar_colors[i],
    # "barProgress": bar_vals[i],
    pollutants_data = []
    for i in range(10):
        d = {
            "name": POLLUTANTS_NAMES[i],
            "abbr": POLLUTANTS_ABBR[i],
            "value": pollutants_vals[i],
            "units": POLLUTANTS_UNITS[i],
            "state": pollutants_states[i],
            "barProgress": bar_vals[i],
            "barColor": bar_colors[i],
            "tipsTitle": POLLUTANTS_TIPS_TITLES[i],
            "tipsContent": POLLUTANTS_TIPS_CONTENTS[i],
            "order": POLLUTANTS_ORDER[i]
        }
        pollutants_data.append(d)

    weather_data = [
        {
            "name": NAME_TEMP,
            "abbr": ABBR_TEMP,
            "value": weather_vals[0],
            "unit": weather_units[0],
            "order": ORDER_TEMP
        },
        {
            "name": NAME_HUMIDITY,
            "abbr": ABBR_HUMIDITY,
            "value": weather_vals[1],
            "unit": weather_units[1],
            "order": ORDER_HUMIDITY
        },
        {
            "name": NAME_PRESSURE,
            "abbr": ABBR_PRESSURE,
            "value": weather_vals[2],
            "unit": weather_units[2],
            "order": ORDER_PRESSURE
        },
        {
            "name": NAME_ALTITUDE,
            "abbr": ABBR_ALTITUDE,
            "value": weather_vals[3],
            "unit": weather_units[3],
            "order": ORDER_ALTITUDE
        },
    ]

    print(pollutants_data)

    data = {
        "pollutantDetails": pollutants_data,
        "weatherDetails": weather_data,
        "locationDetails": location_data,
        "aqi": aqi_val
    }
    print("DATA DATA DATA")
    print(data)
    print("DATA DATA DATA")
    return data


# CSV HOURLY DATA HARI hari
def csv_hourly_data(zipcode, num_of_days=ONE_DAY):
    pollutants_vals = ["N/A"] * NUM_OF_POLLLUTANTS
    pollutants_units = [""] * NUM_OF_POLLLUTANTS
    bar_vals = [0] * NUM_OF_POLLLUTANTS
    bar_colors = ["GREEN"] * NUM_OF_POLLLUTANTS
    pollutants_states = ["N/A"] * NUM_OF_POLLLUTANTS
    weather_vals = ["N/A"] * 4
    weather_units = [""] * 4
    aqi_val = 0

    POLLUTANTS_DATA_AVAILABLE = True
    WEATHER_DATA_AVAILABLE = True

    past_time = datetime.now() - timedelta(days=num_of_days)

    airdata = Air.query.with_entities(
        Air.dustDensity,
        Air.tVOC,
        Air.co2_ppm,
        Air.mq131_o3_ppm,
        Air.mq7_co_ppm,
        Air.mq2_smoke_ppm,
        Air.mq6_lpg_ppm,
        Air.mq4_ng_ppm,
        Air.eCO2,
        Air.mq7_h2_ppm,
        Air.temp,
        Air.humidity,
        Air.pressure,
        Air.altitude,
    ).filter(Air.zipcode == zipcode, Air.timestamp >= past_time).all()

    print(airdata)
    print("^^^^^^^^^^^^^^^^^^")

    air_avgs = airdata[0]

    total_nones = air_avgs.count(None)
    if total_nones == 14:
        POLLUTANTS_DATA_AVAILABLE = False
        WEATHER_DATA_AVAILABLE = False
    else:
        pollut_nones = air_avgs[:10].count(None)
        weather_nones = air_avgs[10:].count(None)

        if pollut_nones == 10:
            POLLUTANTS_DATA_AVAILABLE = False
        if weather_nones == 4:
            WEATHER_DATA_AVAILABLE = False

    if WEATHER_DATA_AVAILABLE:
        # altitude adjustment
        val = air_avgs[13]
        if zipcode == '94720':
            if val < 150:
                val = 177.0
            elif val > 210:
                val = 177.0
        elif zipcode == '95014':
            if val < 180:
                val = 236.0
            elif val > 250:
                val = 236.0
        elif zipcode == '95064':
            if val < 650:
                val = 763.0
            elif val > 850:
                val = 763.0
        elif zipcode == '96150':
            if val < 5500:
                val = 6263.0
            elif val > 6350:
                val = 6263.0
        elif zipcode == '94305':
            if val < 135:
                val = 141.0
            elif val > 155:
                val = 141.0

        weather_vals = [air_avgs[10], air_avgs[11], air_avgs[12], val]
        weather_units = WEATHER_UNITS

    if POLLUTANTS_DATA_AVAILABLE:
        lpgval = air_avgs[6]
        while lpgval > 10:
            lpgval = lpgval / 10

        ng_val = air_avgs[7]

        co_val = air_avgs[4] / 10
        smoke_val = air_avgs[5] / 10

        # PM25, tVOC, CO2, O3, CO, Smoke, LPG, NG, eCO2, H2
        pollutants_vals = [air_avgs[0], air_avgs[1], air_avgs[2], air_avgs[3],
                           co_val, smoke_val, lpgval, ng_val,
                           air_avgs[8], air_avgs[9]]

        print(air_avgs)
        print("------- vals --------")

        # Replacing no2 with co2
        # Replacing so2 with tVOC
        ugm3_pm25 = air_avgs[0]
        ugm3_tvoc = calculate_ugm3(60.9516, air_avgs[1])
        ugm3_co2 = calculate_ugm3(44.01, air_avgs[2])
        ugm3_o3 = calculate_ugm3(48.00, air_avgs[3])
        ugm3_co = calculate_ugm3(28.01, co_val)
        ugm3_pm10 = smoke_val

        final_aqi = (ugm3_co2 * 0.252687954 / 100) + (ugm3_tvoc * 0.400181718 / 10) + (ugm3_o3 * 0.429166667) + (
                ugm3_co * 0.00537414966) + (ugm3_pm25 * 1.248920438) + (ugm3_pm10 * 0.740816327 / 100.0)

        ######aqi_val = air_avgs[0]*1.248920438 + air_avgs[3]*0.429166667 + air_avgs[4]*5.37414966
        # aqi_val = air_avgs[0]*1.248920438 + air_avgs[1]*0.740816327 + air_avgs[2]*0.400181718 + air_avgs[3]*0.429166667
        aqi_val = final_aqi
        aqi_val = round(aqi_val)
        pollutants_units = POLLUTANTS_UNITS
        pollutants_states = []
        bar_colors = []
        bar_vals = []

        # PM2.5
        state, color = get_PM25_state_barColor(pollutants_vals[0])
        pollutants_states.append(state)
        bar_colors.append(color)
        val = get_barValue(air_avgs[0], PM25_max)
        bar_vals.append(val)

        # TVOC
        state, color = get_VOC_state_barColor(air_avgs[1])
        pollutants_states.append(state)
        bar_colors.append(color)
        val = get_barValue(air_avgs[1], tVOC_max)
        bar_vals.append(val)

        # CO2
        state, color = get_CO2_state_barColor(air_avgs[2])
        pollutants_states.append(state)
        bar_colors.append(color)
        val = get_barValue(air_avgs[2], CO2_max)
        bar_vals.append(val)

        # O3
        state, color = get_O3_state_barColor(air_avgs[3])
        pollutants_states.append(state)
        bar_colors.append(color)
        val = get_barValue(air_avgs[3], O3_max)
        bar_vals.append(val)

        # CO
        # state, color = get_CO_state_barColor(air_avgs[4])
        state, color = get_CO_state_barColor(co_val)
        pollutants_states.append(state)
        bar_colors.append(color)
        # val =  get_barValue(air_avgs[4], CO_max)
        val = get_barValue(co_val, CO_max)
        bar_vals.append(val)

        # Smoke
        # state, color = get_Smoke_state_barColor(air_avgs[5])
        state, color = get_Smoke_state_barColor(smoke_val)
        pollutants_states.append(state)
        bar_colors.append(color)
        # val =  get_barValue(air_avgs[5], Smoke_max)
        val = get_barValue(smoke_val, Smoke_max)
        bar_vals.append(val)

        # LPG
        state, color = get_LPG_state_barColor(air_avgs[6])
        pollutants_states.append(state)
        bar_colors.append(color)
        val = get_barValue(air_avgs[6], LPG_max)
        bar_vals.append(val)

        # NG
        # state, color = get_NG_state_barColor(air_avgs[7])
        state, color = get_NG_state_barColor(ng_val)
        pollutants_states.append(state)
        bar_colors.append(color)

        # GAYATRI
        # air_avgs[7] = 10
        val = get_barValue(ng_val, NG_max)
        bar_vals.append(val)

        # eCO2
        state, color = get_eCO2_state_barColor(air_avgs[8])
        pollutants_states.append(state)
        bar_colors.append(color)
        val = get_barValue(air_avgs[8], CO2_max)
        bar_vals.append(val)

        # H2
        state, color = get_H2_state_barColor(air_avgs[9])
        pollutants_states.append(state)
        bar_colors.append(color)
        # PUT H2 MAX
        val = get_barValue(air_avgs[9], CO_max)
        bar_vals.append(val)

    geo = Air.query.with_entities(
        Air.city,
        Air.state,
        Air.country,
        Air.place
    ).filter(Air.zipcode == zipcode).first()

    if geo:
        location_data = {
            "zipCode": zipcode,
            "city": geo[0],
            "state": geo[1],
            "country": geo[2],
            "place": geo[3]
        }
    else:
        location_data = {
            "zipCode": zipcode,
            "city": "N/A",
            "state": "N/A",
            "country": "N/A",
            "place": "N/A"
        }
    pollutants_data = []
    for i in range(10):
        d = {
            "name": POLLUTANTS_NAMES[i],
            "abbr": POLLUTANTS_ABBR[i],
            "value": pollutants_vals[i],
            "units": POLLUTANTS_UNITS[i],
            "state": pollutants_states[i],
            "barProgress": bar_vals[i],
            "barColor": bar_colors[i],
            "tipsTitle": POLLUTANTS_TIPS_TITLES[i],
            "tipsContent": POLLUTANTS_TIPS_CONTENTS[i],
            "order": POLLUTANTS_ORDER[i]
        }
        pollutants_data.append(d)

    weather_data = [
        {
            "name": NAME_TEMP,
            "abbr": ABBR_TEMP,
            "value": weather_vals[0],
            "unit": weather_units[0],
            "order": ORDER_TEMP
        },
        {
            "name": NAME_HUMIDITY,
            "abbr": ABBR_HUMIDITY,
            "value": weather_vals[1],
            "unit": weather_units[1],
            "order": ORDER_HUMIDITY
        },
        {
            "name": NAME_PRESSURE,
            "abbr": ABBR_PRESSURE,
            "value": weather_vals[2],
            "unit": weather_units[2],
            "order": ORDER_PRESSURE
        },
        {
            "name": NAME_ALTITUDE,
            "abbr": ABBR_ALTITUDE,
            "value": weather_vals[3],
            "unit": weather_units[3],
            "order": ORDER_ALTITUDE
        },
    ]

    print(pollutants_data)

    data = {
        "pollutantDetails": pollutants_data,
        "weatherDetails": weather_data,
        "locationDetails": location_data,
        "aqi": aqi_val
    }
    print("DATA DATA DATA")
    print(data)
    print("DATA DATA DATA")
    return data
