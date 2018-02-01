import re
import os
import glob
import pandas as pd

import matplotlib.pyplot as plt

from collections import OrderedDict

fig_size = [12, 9]
plt.rcParams["figure.figsize"] = fig_size


def parse_filepath(string):
    head, tail = os.path.split(string)
    return re.search(r'_(.*),', tail).group(1)


def load_csv_files(path, index_column='Step', wanted_columns=[1, 2], skip_rows=2):
    expanded_path = os.path.abspath(path)
    csv_filepaths = glob.glob(os.path.join(expanded_path, '*.csv'))
    dataframe_from_each_file = (pd.read_csv(filepath,
                                            index_col=index_column,
                                            names=['Wall time', 'Step', parse_filepath(filepath)],
                                            skiprows=skip_rows,
                                            header=None,
                                            usecols=wanted_columns)
                                for filepath in csv_filepaths)
    concatenated_dataframe = pd.concat(dataframe_from_each_file, axis=1, join='inner')
    return concatenated_dataframe


experiment_logs = load_csv_files('./experiment_results/mnist_losses')


def add_rolling_average(dataframe, window=6):
    for column in dataframe:
        dataframe[f'{column}_rolling_average'] = dataframe[column].rolling(window=window).mean()


add_rolling_average(experiment_logs)

colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan']


def graph_experiment_losses(dataframe, number_of_logs=4, filters=('average')):
    fig = plt.figure()
    ax = fig.add_subplot()
    axes = experiment_logs.plot(ax=ax, color=colors[:number_of_logs], logy=True, sort_columns=True)
    axes.set_xlabel('Step', fontsize=16)
    axes.set_ylabel('Training Loss', fontsize=16)
    axes.spines["top"].set_visible(False)
    axes.spines["bottom"].set_visible(False)
    axes.spines["right"].set_visible(False)
    axes.spines["left"].set_visible(False)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    for i in range(number_of_logs):
        axes.lines[i].set_alpha(0.3)
        axes.lines[i].set_alpha(0.3)
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = OrderedDict((label, handel) for label, handel in zip(labels, handles) if not label.endswith(filters))
    legend = plt.legend(by_label.values(),by_label.keys(), frameon=False, prop={'size': 12})
    for leg in legend.legendHandles:
        leg.set_alpha(1)


graph_experiment_losses(experiment_logs)

plt.savefig('losses.png', format='png', bbox_inches='tight')