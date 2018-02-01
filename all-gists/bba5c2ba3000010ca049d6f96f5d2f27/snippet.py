import numpy as np
import matplotlib.pyplot as plt
from jr.plot import pretty_plot, plot_eb  # available @ http://github.com/kingjr/jr-tools

# make up data
x = np.linspace(1., 5., 100)
all_data = dict(AG=np.sin(x), V1=np.cos(x), IPS=np.cos(x + 1.5))

# choose color manually
colors = ['r', [.1, 1., .2, 1.], 'b']
alphas = [.35, .5, .35]
fig, ax = plt.subplots(1)
for (name, data), color, alpha in zip(all_data.iteritems(), colors, alphas):
    plot_eb(x, data, .2, color=color, ax=ax, alpha=alpha)
    ax.plot(x, data, color='k', linewidth=1.2)

# make it pretty
ax.spines['bottom'].set_position('center')
ax.set_yticks(np.arange(-1, 1.01, 1))
ax.set_xticks(np.arange(1, 5.01, 1))
ax.set_xticklabels([])
pretty_plot(ax)