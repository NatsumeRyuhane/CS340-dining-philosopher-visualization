import matplotlib.pyplot as plt
import numpy as np
import time
from colour import Color

# Set color scheme
def draw(data):

    max_time = 0
    label = []
    status_type = 1
    status = []
    count = 0
    for i in data:
        label.append(f"P{count}")
        if (len(i) > status_type):
            status_type = len(i)
            status = list(i.keys())

        for j in i.items():
            if (j[1] > max_time): max_time = j[1]

        count += 1

    col_s = Color("red")
    colors = list(col_s.range_to(Color("purple"), status_type))
    colors = [color.rgb for color in colors]

    draw_data = {}
    for j in status:
        draw_data[j] = []

    del(draw_data[99])

    for s in range(0, len(status)):
        if (status[s] == 99) : continue
        try:
            current_draw_stat = status[s]
        except IndexError: continue

        try:
            next_draw_stat = status[s + 1]
        except IndexError: next_draw_stat = None

        for i in range(0, len(data)):
            if next_draw_stat is None:
                draw_data[current_draw_stat].append(round(max_time - data[i][current_draw_stat], 2))
            else:
                draw_data[current_draw_stat].append(round(data[i][next_draw_stat] - data[i][current_draw_stat], 2))

    count = 0
    prev = None
    curr = None
    for d in draw_data:
        curr = draw_data[d]
        if prev is None:
            plt.barh(label, curr, color = colors[count])
            prev = curr
        else:
            plt.barh(label, curr, left = prev, color=colors[count])

            for i in range(0, len(prev)):
                try:
                    prev[i] += curr[i]
                except IndexError: continue

        count += 1

    plt.show()
    pass