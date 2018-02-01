# Create a random palette in LAB space and convert to RGB.
# For easy use as a infinite colormap in matplotlib.
# After an idea from @amueller and
# http://stackoverflow.com/questions/10254207/color-and-line-writing-using-matplotlib

import numpy as np
from colormath.color_objects import LabColor


def get_random_color(seed=3):
    rstate = np.random.RandomState(seed)
    while True:
        # select colors which are neither too dark nor too bright
        # whole range is 0:100
        lab_l = rstate.uniform(20, 80)

        # I determined these limits empirically by converting random RGB
        # coordinates to lab:
        lab_a = rstate.uniform(-85, 100)
        lab_b = rstate.uniform(-106, 92)

        #col = [int(x) for x in colorsys.hsv_to_rgb(hue, 1.0, 230)]
        col = LabColor(lab_l, lab_a, lab_b).convert_to("rgb", debug=False)
        yield "#{0:02x}{1:02x}{2:02x}".format(col.rgb_r, col.rgb_g, col.rgb_b)


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    x = 0.3 * np.arange(40)
    for idx, c in zip(xrange(5), get_random_color()):
        y = np.exp2(x + 0.5 * idx)
        z = np.polyfit(x, y, 6)
        p = np.poly1d(z)

        plt.scatter(x, y, color=c, marker='o')
        plt.plot(x, p(x), '-', color=c, label=str(idx))

    plt.legend()
    plt.show()