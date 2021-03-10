
NUM_OF_POLLLUTANTS = 10
NUM_OF_WEATHER_COMP = 4

# RL values
MQ2_RL = 10
MQ4_RL = 20
MQ6_RL = 20
MQ7_RL = 20
MQ131_RL = 10

# Taking initial Cupertino readings as Ro
MQ2_Ref_Ro = 6.69
MQ4_Ref_Ro = 78.02
MQ6_Ref_Ro = 7.01
MQ7_Ref_Ro = 8.22
MQ131_Ref_Ro = 85.71

dust_Voc = 0.03
print("P2")

MQ2_LPGCurve = [2.3, 0.21, -0.47]
MQ2_COCurve = [2.3, 0.72, -0.34]
MQ2_SmokeCurve = [2.3, 0.53, -0.44]
MQ4_MethaneCurve = [2.254, -0.224, -0.077]
MQ6_LPGCurve = [2.301, 0.307, -0.422]
MQ7_COCurve = [1.699, 0.201, -0.651]
MQ7_H2Curve = [1.699, 0.087, -0.729]
MQ131_O3Curve = [0.692, 0.608, -0.900]

DAYS = "days"
HOURS = "hours"
ONE_HOUR = 1
ONE_DAY = 1
ONE_WEEK = 7
ONE_MONTH = 30
TWO_MONTH = 60
THREE_MONTH = 90
# TIMESERIES_QUARTER = 90
TIMESERIES_QUARTER = 60
PM25 = "pm25"
tVOC = "tVOC"
CO2 = "co2"
O3 = "o3"
TEMP = "temp"
HUMIDITY = "humidity"
TS_THRESHOLDS_JSON = "ts_thresholds.json"

NAME_PM25 = "Particulate Matter"
ABBR_PM25 = "PM2.5"
UNITS_PM25 = "ug/m3"
ORDER_PM25 = 1
CONTENT_PM25 = '<ul><li>Avoid smoke, burning wood, candles, incense, etc.</li><li>Ventilate and use exhaust fans</li><li>Use exhaust fan while cooking</li><li>Use HEPA filters to purify air</li><li><a href="https://www.airnow.gov/aqi/aqi-basics/extremely-high-levels-of-pm25" target="_blank">Further Reading</a></li></ul><p style="padding-left: 30px;">Thresholds (ug/m3):<br />&bull; Good: 0-12<br />&bull; Average: 12-15<br />&bull; Poor: 15-35<br />&bull; Bad: &gt;35</p>'

NAME_TVOC = "Volatile Organic Compounds"
ABBR_TVOC = "VOC"
UNITS_TVOC = "ppb"
ORDER_TVOC = 2
CONTENT_TVOC = '<ul><li>Ventilate</li><li>Reduce use of spray cosmetics, perfumes, air fresheners, aerosols</li><li>Ventilate while using soaps, cleaning solvents, paints, nail polish removers</li><li><a href="https://thegreendivas.com/2015/06/12/16-ways-to-reduce-exposure-to-off-gassing-vocs-infographic" target="_blank">Further Reading</a></li></ul><p style="padding-left: 30px;">Thresholds (ppb):<br />&bull; Good: 0-220<br />&bull; Average: 221-660<br />&bull; Poor: 661-2000<br />&bull; Bad: &gt;2000</p>'

NAME_CO2 = "Carbon Dioxide"
ABBR_CO2 = "CO2"
UNITS_CO2 = "ppm"
ORDER_CO2 = 3
CONTENT_CO2 = '<ul><li>Ventilate, especially while cooking and in gatherings</li><li>Get houseplants</li><li>Avoid smoke</li><li><a href="https://learn.kaiterra.com/en/air-academy/tips-for-reducing-co2" target="_blank">Further Reading</a></li></ul><p style="padding-left: 30px;">Thresholds (ppm):<br />&bull; Good: 350-1000<br />&bull; Average: 1001-2000<br />&bull; Poor: 2001-5000<br />&bull; Bad: &gt;5000</p>'

NAME_O3 = "Ozone"
ABBR_O3 = "O3"
UNITS_O3 = "ppm"
ORDER_O3 = 4
CONTENT_O3 = '<ul><li>Check your air purifier to see if it adds or removes ozone</li><li>Use activated carbon air filters</li><li>Get houseplants that absorb ozone</li><li><a href="https://www.sciencedaily.com/releases/2009/09/090908103634.htm" target="_blank">Further Reading</a></li></ul><p style="padding-left: 30px;">Thresholds (ppm):<br />&bull; Good: < 0.06<br />&bull; Average: < 0.09<br />&bull; Poor: < 0.20<br />&bull; Bad: &gt;=0.20</p>'

NAME_CO = "Carbon Monoxide"
ABBR_CO = "CO"
UNITS_CO = "ppm"
ORDER_CO = 5
CONTENT_CO = '<ul><li>Ventilate</li><li>Avoid smoke</li><li>Have appliances and heating systems serviced</li><li>Don&rsquo;t run car engine in garage</li><li><a href="https://www.health.harvard.edu/blog/keeping-carbon-monoxide-out-2018012213141" target="_blank">Further Reading</a></li></ul><p style="padding-left: 30px;">Thresholds (ppm):<br />&bull; Good: 0-3<br />&bull; Average: 3-8<br />&bull; Poor: 8-10<br />&bull; Bad: &gt;10</p>'

NAME_SMOKE = "PM10"
ABBR_SMOKE = ""
UNITS_SMOKE = "ug/m3"
ORDER_SMOKE = 6
CONTENT_SMOKE = '<ul><li>Seek out the source of smoke and stop</li><li>Close windows and doors to avoid outside smoke</li><li>Avoid smoking indoors</li><li>Avoid smoke-producing cooking indoors</li><li>Use a HEPA filter air purifier</li><li>Further reading:&nbsp;<a href="https://homeairguides.com/air/10-ways-for-how-to-protect-yourself-from-wildfire-smoke" target="_blank">https://homeairguides.com/air/10-ways-for-how-to-protect-yourself-from-wildfire-smoke</a></li></ul><p style="padding-left: 30px;">Thresholds (ug/m3):<br />&bull; Good: 0-54<br />&bull; Average: 55-254<br />&bull; Poor: 255-424<br />&bull; Bad: &gt;424</p>'

NAME_LPG = "Liquid Petroleum Gas"
ABBR_LPG = "LPG"
UNITS_LPG = "ppm"
ORDER_LPG = 7
CONTENT_LPG = '<ul><li>Leave area of suspected leak as quickly as possible</li><li>Warn others to stay out of the area</li><li>Call local utility or just 911</li><li>Further reading:&nbsp;<a href="https://www.peoples-gas.com/all-about-gas/safety/smell/what-to-do.php" target="_blank">https://www.peoples-gas.com/all-about-gas/safety/smell/what-to-do.php</a></li></ul>'

NAME_NG = "Natural Gas"
ABBR_NG = "NG"
UNITS_NG = "ppm"
ORDER_NG = 8
CONTENT_NG = '<ul><li>Leave area of suspected leak as quickly as possible</li><li>Warn others to stay out of the area</li><li>Call local utility preferably or 911</li><li>Further reading:&nbsp;<a href="https://www.peoples-gas.com/all-about-gas/safety/smell/what-to-do.php" target="_blank">https://www.peoples-gas.com/all-about-gas/safety/smell/what-to-do.php</a></li></ul>'

NAME_eCO2 = "Equivalent Carbon Dioxide"
ABBR_eCO2 = "eCO2"
UNITS_eCO2 = "ppm"
ORDER_eCO2 = 9
CONTENT_eCO2 = '<ul><li>Wear a Mask</li><li>Avoid Crowded Places</li></ul>'

NAME_H2 = "Hydrogen"
ABBR_H2 = "H2"
UNITS_H2 = "ppm"
ORDER_H2 = 10
CONTENT_H2 = '<ul><li>Wear a Mask</li><li>Avoid Crowded Places</li></ul>'

NAME_TEMP = "Temperature"
ABBR_TEMP = "Temperature"
UNITS_TEMP = "F"
ORDER_TEMP = 1

NAME_HUMIDITY = "Humidity"
ABBR_HUMIDITY = "Humidity"
UNITS_HUMIDITY = "%"
ORDER_HUMIDITY = 1

NAME_PRESSURE = "Pressure"
ABBR_PRESSURE = "Pressure"
UNITS_PRESSURE = "inHg"
ORDER_PRESSURE = 3

NAME_ALTITUDE = "Altitude"
ABBR_ALTITUDE = "Altitude"
UNITS_ALTITUDE = "ft"
ORDER_ALTITUDE = 4

POLLUTANTS_NAMES = [NAME_PM25, NAME_TVOC, NAME_CO2, NAME_O3, NAME_CO,
                    NAME_SMOKE, NAME_LPG, NAME_NG, NAME_eCO2, NAME_H2]

POLLUTANTS_ABBR = [ABBR_PM25, ABBR_TVOC, ABBR_CO2, ABBR_O3, ABBR_CO,
                   ABBR_SMOKE, ABBR_LPG, ABBR_NG, ABBR_eCO2, ABBR_H2]

POLLUTANTS_UNITS = [UNITS_PM25, UNITS_TVOC, UNITS_CO2, UNITS_O3, UNITS_CO,
                    UNITS_SMOKE, UNITS_LPG, UNITS_NG, UNITS_eCO2, UNITS_H2]

POLLUTANTS_UNITS_EMPTY = ["", "", "", "", "",
                          "", "", "", "", ""]

POLLUTANTS_ORDER = [ORDER_PM25, ORDER_TVOC, ORDER_CO2, ORDER_O3, ORDER_CO,
                    ORDER_SMOKE, ORDER_LPG, ORDER_NG, ORDER_eCO2, ORDER_H2]

POLLUTANTS_TIPS_TITLES = [ABBR_PM25, ABBR_TVOC, ABBR_CO2, ABBR_O3, ABBR_CO,
                          NAME_SMOKE, ABBR_LPG, ABBR_NG, ABBR_eCO2, ABBR_H2]

POLLUTANTS_TIPS_CONTENTS = [CONTENT_PM25, CONTENT_TVOC, CONTENT_CO2, CONTENT_O3, CONTENT_CO,
                            CONTENT_SMOKE, CONTENT_LPG, CONTENT_NG, CONTENT_eCO2, CONTENT_H2]

WEATHER_UNITS = [UNITS_TEMP, UNITS_HUMIDITY, UNITS_PRESSURE, UNITS_ALTITUDE]
NUM_OF_POLLLUTANTS = 10
NUM_OF_WEATHER_COMP = 4