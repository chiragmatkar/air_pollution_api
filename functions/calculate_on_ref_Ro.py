import datetime


def calculate_on_ref_Ro(sensor_raw, sensor_RL, sensor_ref_Ro, sensor_curve):
    sensor_rs = MQResistanceCalculation(sensor_raw, sensor_RL)
    sensor_rs_by_ro = (float)(sensor_rs) / sensor_ref_Ro
    sensor_ppm = MQGetPercentage(sensor_rs_by_ro, sensor_curve)

    return sensor_ppm


'''
MQResistanceCalculation
Input:   raw_adc - raw value read from adc, which represents the voltage
Output:  the calculated sensor resistance
Remarks: The sensor and the load resistor forms a voltage divider.
         Given the voltage across the load resistor and its resistance,
         the resistance of the sensor could be derived.

'''


def MQResistanceCalculation(raw_adc, rl_value):
    return (((float)(rl_value) * (1023 - raw_adc) / raw_adc))



'''
MQGetPercentage
Input:   rs_ro_ratio - Rs divided by Ro
         pcurve      - pointer to the curve of the target gas
Output:  ppm of the target gas
Remarks: By using the slope and a point of the line.
         The x(logarithmic value of ppm) of the line could be derived
         if y(rs_ro_ratio) is provided. As it is a logarithmic coordinate,
         power of 10 is used to convert the result to non-logarithmic value.

'''

GREEN = "green"
BLUE = "blue"
ORANGE = "orange"
RED = "red"

GOOD = "GOOD"
MODERATE = "MODERATE"
POOR = "POOR"
BAD = "BAD"

'''
def get_Smoke_state_barColor(val):
    if 0 <= val < 201:
        return GOOD, GREEN
    elif 201 < val < 401:
        return MODERATE, BLUE
    elif 401 <= val < 601:
        return POOR, ORANGE
    elif val >= 600:
        return BAD, RED
'''


def get_temp_state_barColor(val):
    if 20 <= val <= 27:
        return GOOD, GREEN
    elif (16 <= val < 20) or (27 <= val <= 28):
        return MODERATE, BLUE
    elif (28 < val <= 30):
        return POOR, ORANGE
    elif val < 16 or val > 30:
        return BAD, RED


def get_humidity_state_barColor(val):
    if 30 <= val <= 50:
        return GOOD, GREEN
    elif 51 <= val <= 60:
        return MODERATE, BLUE
    elif (20 < val < 30) or (60 < val < 70):
        return POOR, ORANGE
    elif val < 20 or val > 70:
        return BAD, RED


def get_PM25_state_barColor(val):
    if 0 <= val < 13:
        return GOOD, GREEN
    elif 13 <= val < 16:
        return MODERATE, BLUE
    elif 16 <= val < 36:
        return POOR, ORANGE
    elif val >= 36:
        return BAD, RED


def get_VOC_state_barColor(val):
    if 0 <= val < 221:
        return GOOD, GREEN
    elif 221 <= val < 661:
        return MODERATE, BLUE
    elif 661 <= val < 2001:
        return POOR, ORANGE
    elif val >= 2001:
        return BAD, RED


def get_CO2_state_barColor(val):
    if 250 <= val < 1001:
        return GOOD, GREEN
    elif 1001 <= val < 2001:
        return MODERATE, BLUE
    elif 2001 <= val < 5001:
        return POOR, ORANGE
    elif val >= 5001:
        return BAD, RED


def get_O3_state_barColor(val):
    if 0 <= val < 0.06:
        return GOOD, GREEN
    elif 0.06 <= val < 0.09:
        return MODERATE, BLUE
    elif 0.09 <= val < 0.2:
        return POOR, ORANGE
    elif val >= 0.2:
        return BAD, RED


def get_CO_state_barColor(val):
    if 0 <= val < 4:
        return GOOD, GREEN
    elif 4 <= val < 9:
        return MODERATE, BLUE
    elif 9 <= val < 11:
        return POOR, ORANGE
    elif val >= 11:
        return BAD, RED


def get_Smoke_state_barColor(val):
    if 0 <= val < 55:
        return GOOD, GREEN
    elif 55 < val < 255:
        return MODERATE, BLUE
    elif 255 <= val < 425:
        return POOR, ORANGE
    elif val >= 425:
        return BAD, RED


def get_LPG_state_barColor(val):
    if 0 <= val < 21:
        return GOOD, GREEN
    elif 21 <= val < 36:
        return MODERATE, BLUE
    elif 36 <= val < 61:
        return POOR, ORANGE
    elif val >= 61:
        return BAD, RED


def get_NG_state_barColor(val):
    if 0 <= val < 21:
        return GOOD, GREEN
    elif 21 <= val < 36:
        return MODERATE, BLUE
    elif 36 <= val < 61:
        return POOR, ORANGE
    elif val >= 61:
        return BAD, RED


def get_eCO2_state_barColor(val):
    if 250 <= val < 1001:
        return GOOD, GREEN
    elif 1001 <= val < 2001:
        return MODERATE, BLUE
    elif 2001 <= val < 5001:
        return POOR, ORANGE
    elif val >= 5001:
        return BAD, RED


def get_H2_state_barColor(val):
    if 0 <= val < 4:
        return GOOD, GREEN
    elif 4 <= val < 9:
        return MODERATE, BLUE
    elif 9 <= val < 11:
        return POOR, ORANGE
    elif val >= 11:
        return BAD, RED


humidity_max = 70
temp_max = 30
PM25_max = 35
tVOC_max = 2000
O3_max = 0.2
CO2_max = 5000
CO_max = 50
Smoke_max = 610
NG_max = 100
LPG_max = 100

'''
Smoke_max = 5000
NG_max = 5000
LPG_max = 5000
'''


# returns in multiples of 10. 0-100, including both
def get_barValue(value, maxValue):
    # return Math.min(Math.round(value / maxValue * 10) * 10, 100)
    value = min(math.floor(float(value) / maxValue * 10) * 10, 100)
    print(value)
    if value < 1:
        value = 5

    return value


def MQGetPercentage(rs_ro_ratio, pcurve):
    # Python program explaining
    # log() function
    val1 = np.log(rs_ro_ratio)
    numerator = val1 - pcurve[1]
    fraction = float(numerator) / pcurve[2]
    exponent = fraction + pcurve[0]
    base = 10

    result = base ** exponent
    return result


def parse_date(date_str):
    yyyy_mm_dd = date_str.split('-')
    yyyy = int(yyyy_mm_dd[0])
    mm = int(yyyy_mm_dd[1])
    dd = int(yyyy_mm_dd[2])
    date_obj = date(year=yyyy, month=mm, day=dd)

    return date_obj


def create_datetime_obj(datestr, delimiter=" "):
    # An example input string: '2019-12-23 10:23:14.472074'
    # Example 2: 2019-12-21T05:01:49.542965+00:00
    ds = datestr.split(delimiter)

    # creates YYYY MM DD tokens
    # Example: ['2019', '12', '23']
    date_tokens = ds[0].split("-")
    yyyy = int(date_tokens[0])
    mm = int(date_tokens[1])
    dd = int(date_tokens[2])

    time_str_tokens = ds[1].split("+")

    # Example: ['10', '23', '14.472074']
    time_tokens = time_str_tokens[0].split(":")
    hr = int(time_tokens[0])
    mn = int(time_tokens[1])

    # Example: ['14', '472074']
    time_sec_tokens = time_tokens[2].split(".")
    sec = int(time_sec_tokens[0])
    ms = int(time_sec_tokens[1])

    # print ("{} {} {} {} {} {} {}".format(yyyy, mm, dd, hr, mn, sec, ms))
    # datetime(year, month, day, hour, minute, second, microsecond)
    datetime_obj = datetime(yyyy, mm, dd, hr, mn, sec, ms)

    return datetime_obj


