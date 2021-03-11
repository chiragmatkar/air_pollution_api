from flask import request
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import MO, TU, WE, TH, FR, SA
from config import app


def plot_timeseries(data, name, unit, zipcode, current_time, lines_data=None):
    # plot data
    print("^%^%^%^%^%^%^%^%^%^%")
    print("ENTER plot_timeseries")
    print("^%^%^%^%^%^%^%^%^%^%")

    fig, ax = plt.subplots(figsize=(25, 7))

    num_of_data_points = data[data.columns[0]].count()
    print("num_of_data_points")
    print(num_of_data_points)

    data.plot(ax=ax)
    ax.grid(True, which='both')

    # set margin, labels and font size
    y_label = "{} {}".format(name, unit)
    plt.margins(x=0)
    plt.xlabel('Timestamps', size=24)
    plt.ylabel(y_label, size=24)
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)

    # set ticks every Mon and Fri
    # loc = mdates.WeekdayLocator(byweekday=(MO,FR))

    if num_of_data_points < 1000:
        loc = mdates.WeekdayLocator(byweekday=(MO, FR))
    elif num_of_data_points < 2000:
        loc = mdates.WeekdayLocator(byweekday=(MO))
    elif num_of_data_points < 3000:
        loc = mdates.WeekdayLocator(byweekday=MO, interval=2)
    else:
        loc = mdates.WeekdayLocator(byweekday=MO, interval=3)
    print("LOC LOC LOC")
    print(loc)
    print("LOC LOC LOC")
    ax.xaxis.set_major_locator(loc)

    # plot the threshold value lines
    for line_data in lines_data:
        plt.axhline(line_data["value"], color=line_data["color"])

    # save plot
    file_name = "{}_{}_{}.png".format(name, zipcode, current_time)
    file_name_path = "{}/{}".format(app.config["CLIENT_GRAPHS"], file_name)
    plt.savefig(file_name_path)

    # graph URL
    graph_url = "{}/{}".format(request.url, file_name)
    print("^%^%^%^%^%^%^%^%^%^%")
    print("Exiting plot_timeseries")
    print(graph_url)
    print("^%^%^%^%^%^%^%^%^%^%")
    return graph_url

