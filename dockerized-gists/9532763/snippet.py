#!/usr/bin/env python
"""
Create SPC charts from data sets. Inspired by Simon Guilfoyle's
"Intelligent Policing" http://amzn.to/1dNNCfb

The algorithm described by Guilfoyle in the book is:

Given a list of data points sorted in chronological order, iterate
over the list starting at index 1 (that is, skip the last entry in
the list), subtracting each value from the previous value. The
resulting list of values is the "set of ranges."

Take the median value from the set of ranges, and multiply it by
3.14. This is the "distance from the center line to the control
limits."

Find the average of all the data points in the original list. The
average of the data series is the "center line of the control chart."

Now plot the original data series and draw:

1. a solid line at the average

2. Two dashed lines that are "distance from the center line to the control
   limits" units above and below the center line, respectively.
"""

import sys
import hashlib
import numpy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def calculate_ranges(values):
    accumulator = []
    for count, x in enumerate(values):
        ++count

        if (count + 1) < len(values):
            range =  x - values[count + 1]
            accumulator.append(abs(range))

    return accumulator

def make_plot(values):
    low_water_mark = min(values)
    high_water_mark = max(values)
    use_log_scale = False

    if (high_water_mark - low_water_mark) > 1000:
        use_log_scale = True

    ranges = calculate_ranges(values)
    raw_median_range = numpy.median(ranges)

    if raw_median_range > 1 or raw_median_range < -1 :
        median_of_ranges = abs(raw_median_range)
    else:
        median_of_ranges = 1

    avg_value = numpy.average(values)

    upper_limit = median_of_ranges * 3.14 + avg_value

    lower_limit = avg_value - median_of_ranges * 3.14

    stdout_filehandle = sys.stdout
    sys.stdout = sys.stderr

    print('ranges: {}'.format(sorted(ranges)))
    print('median range: {}'.format(raw_median_range))
    print('upper control limit: {}'.format(upper_limit))
    print('lower control limit: {}'.format(lower_limit))

    sys.stdout = stdout_filehandle

    plt.plot(values, 'ko')

    plt.axhline(
        y=avg_value,
        color="#666666",
        )

    plt.annotate(
        '{0:g}'.format(avg_value),
        xy=(1, avg_value),
        xytext=(8, 0),
        xycoords=('axes fraction', 'data'),
        textcoords='offset points',
        va='center',
        color="#333333"
        )

    plt.axhline(
        y=upper_limit,
        color="#333333",
        linestyle=':'
        )

    plt.annotate(
        '{0:g}'.format(upper_limit),
        xy=(1, upper_limit),
        xytext=(8, 0),
        xycoords=('axes fraction', 'data'),
        textcoords='offset points',
        va='center',
        color="#333333"
        )

    if lower_limit > 0:
        plt.axhline(
            y=lower_limit,
            color="#333333",
            linestyle=':'
            )

    if lower_limit > 0:
        plt.annotate(
            '{0:g}'.format(lower_limit),
            xy=(1, lower_limit),
            xytext=(8, 0),
            xycoords=('axes fraction', 'data'),
            textcoords='offset points',
            va='center',
            color="#333333"
            )

def plot_integers(raw_values):
    values = [float(s) for s in raw_values]
    make_plot(values)

def get_inputs():
    if len(sys.argv) > 1:
        sys.argv.pop(0)

        if len(sys.argv) == 1:
            return sys.argv[0].strip().split('\n')
        else:
            return sys.argv
    else:
        raw_input = sys.stdin.readlines()
        if len(raw_input) == 1:
            return raw_input[0].strip().split(' ')
        else:
            return raw_input

"""
Only so many labels fit comfortably along the y-axis. After that,
downsample the labels so that we only print as many as will fit. Don't
attempt to be smart about which labels to filter, just use the overall
count of labels as a guide.
"""
def sample_from_labels(labels):
    labels_that_can_fit_on_the_y_axis = 40
    filtered_labels = []
    if (len(labels) > labels_that_can_fit_on_the_y_axis):
        filtered_labels = filter_for_labels(labels_that_can_fit_on_the_y_axis, labels)
    else:
        filtered_labels = labels
    return filtered_labels

def filter_for_labels(labels_that_can_fit_on_the_y_axis, labels):
    filtered_labels = []
    every_nth_label = len(labels) / (labels_that_can_fit_on_the_y_axis / 2)
    for index, label in enumerate(labels):
        if (index + 1) == len(labels):
            filtered_labels.append(label)
        elif index % every_nth_label != 0 or (len(labels) - index + 1) < every_nth_label :
            filtered_labels.append(' ')
        else:
            filtered_labels.append(label)

    return filtered_labels

def spc_chart_cli():
    raw_values = get_inputs()

    if len(raw_values) > 1 and len(raw_values[0].split()) > 1:
        values = []
        labels = []

        for s in raw_values:
            tokens = s.strip().split()
            cons = tokens.pop(0)
            cdr = ' '.join(tokens)
            values.append(float(cons))
            labels.append(cdr)

        labels = sample_from_labels(labels)

        make_plot(values)
        plt.xticks(range(len(values)), labels, size='small', rotation=75)

    elif len(raw_values) > 1:
        plot_integers(raw_values)

    else:
        plot_integers(raw_values[0].split())

    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(13.5, 8)

    guid = hashlib.sha1(''.join(raw_values)).hexdigest()

    file_name='./spc-chart-' + guid + '.png'

    fig.savefig(file_name, dpi=300, bbox_inches='tight')

    print(file_name)

spc_chart_cli()
