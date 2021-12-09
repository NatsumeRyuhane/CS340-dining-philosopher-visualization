import matplotlib.pyplot as plt
import numpy as np
import time
from colour import Color

# Set color scheme
def draw(data, max_time):

    label = []
    base = []

    status_type_count = 1
    status_list = []


    count = 0
    for i in data:
        label.append(f"P{count}")

        base.append(i["THINKING"])

        if (len(i) > status_type_count):
            status_type_count = len(i)
            status_list = list(i.keys())

        count += 1

    # generate color schema
    col_s = Color("green")
    colors = list(col_s.range_to(Color("blue"), status_type_count))
    colors = [color.rgb for color in colors]

    # generate draw data
    draw_data = {}
    for j in status_list:
        draw_data[j] = []

    try:
        del(draw_data["FINISHED"])
    except KeyError: pass

    for s in range(0, len(status_list)):
        # finish drawing on FINISHED state
        if (status_list[s] == "FINISHED"): break

        current_draw_stat = status_list[s]

        try:
            next_draw_stat = status_list[s + 1]
        except IndexError:
            next_draw_stat = None

        for i in range(0, len(data)):
            if (current_draw_stat in data[i]):
                if (next_draw_stat in data[i]) and (next_draw_stat is not None):
                    elapsed_time = round(data[i][next_draw_stat] - data[i][current_draw_stat], 2)
                    draw_data[current_draw_stat].append(elapsed_time)
                else:
                    try:
                        next_draw_stat_tmp = status_list[s + 2]
                        elapsed_time = round(data[i][next_draw_stat_tmp] - data[i][current_draw_stat], 2)
                    except IndexError or KeyError:
                        elapsed_time = round(max_time - data[i][current_draw_stat], 2)

                    draw_data[current_draw_stat].append(elapsed_time)
            else:
                draw_data[current_draw_stat].append(0)

    count = 0
    prev_list = base
    curr = None

    for d in draw_data:
        curr = draw_data[d]

        plt.barh(label, curr, left = prev_list, color=colors[count])

        for i in range(0, len(prev_list)):
            try:
                prev_list[i] += curr[i]
            except IndexError: continue

        count += 1

    plt.legend(status_list)
    plt.show()