def plot_two_hists(var, df1, df2, title1, title2, xlabel, ylabel, **kwargs):
    """function to make 2 side-by-side hists to compare 2 dataframes"""
    fig2, ax2 = plt.subplots(nrows=1, ncols=2)
    fig2.set_size_inches(24, 8)
    plt.subplots_adjust(wspace=0.2)
    
    df1[var].plot(kind="hist", ax=ax2[0], title=title1, **kwargs)
    ax2[0].set_xlabel(xlabel)
    ax2[0].set_ylabel(ylabel)

    df2[var].plot(kind="hist", ax=ax2[1], title=title2, **kwargs)
    ax2[1].set_xlabel(xlabel)
    ax2[1].set_ylabel(ylabel)

    # set range of both y axis to cover smallest minimum, largest maximum
    miny = min(ax2[0].get_ylim()[0], ax2[1].get_ylim()[0])
    maxy = max(ax2[0].get_ylim()[1], ax2[1].get_ylim()[1])
    for ax in ax2:
        ax.set_ylim([miny, maxy])

    return fig2, ax2


# In[92]:

def plot_two_scatters(varx, vary, df1, df2, title1, title2, xlabel, ylabel, **kwargs):
    """function to make 2 side-by-side scatter plots to compare 2 dataframes"""
    fig2, ax2 = plt.subplots(nrows=1, ncols=2)
    fig2.set_size_inches(24, 8)
    plt.subplots_adjust(wspace=0.2)
    
    df1.plot(kind=scat, x=varx, y=vary, ax=ax2[0], title=title1, **kwargs)
    ax2[0].set_xlabel(xlabel)
    ax2[0].set_ylabel(ylabel)

    df2.plot(kind=scat, x=varx, y=vary, ax=ax2[1], title=title2, **kwargs)
    ax2[1].set_xlabel(xlabel)
    ax2[1].set_ylabel(ylabel)

    return fig2, ax2