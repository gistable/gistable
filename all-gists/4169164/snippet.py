import pandas as pd
import matplotlib.pyplot as plt

def combined_label(perc, tot):
    """
    Format a label to include by Euros and %.
    """
    return "{0:,.0f}k EUR, {1:.0f}%".format(perc * tot / 1000, perc * 100)

def cost_cum(data, focus, subject):
    """
    Accumulate the stats.
    - data is a DataFrame, 
    - focus is the colum to group by
    - subject is the column to aggregate.
    """
    # Setup data frame
    parts = data[[focus, 'cost']].groupby(focus).sum().sort(subject, ascending=False)
    parts['percent'] = parts['cost'] / parts.cost.sum()
    parts['cum_percent'] = parts['percent'].cumsum()
    return parts

def cost_pareto(data, focus_name, limit_percent = 0.75):
    # Filter and organize the data frame
    top_parts = data[data['cum_percent'] < limit_percent]
    top_parts.set_index(top_parts['percent'])
    
    # Draw the plots
    fig = plt.figure(figsize=(10,7))
    fig.subplots_adjust(bottom=0.4, left=0.15)
    ax = fig.add_subplot(1,1,1)
    top_parts['cum_percent'].plot(ax=ax, color="k", drawstyle="steps-post")
    top_parts['percent'].plot(ax=ax, kind="bar", color="k", alpha=0.5)
    ax.set_ylim(bottom=0, top=1)
    tick_nums = [x/float(100) for x in range(0,101,20)]
    ax.set_yticks(tick_nums)
    tot_cost = top_parts['cost'].sum()
    ax.set_yticklabels([combined_label(x, tot_cost) for x in tick_nums])
    ax.set_title("Top %s%% of Cost Split By %s" % (int(limit_percent * 100), focus))
    ax.set_xlabel("")
    return ax

accumulated = cost_cum(data, 'Part', 'Cost')
chart = cost_pareto(accumulated, 'Part', 0.9)