def plot_correlogram(df,figsize=(20,20)):
    ''' Creat an n x n matrix of scatter plots for every
    combination of numeric columns in a dataframe'''

    cols = list(df.columns[df.dtypes=='float64'])
    n = len(cols)
    fig, ax = plt.subplots(n,n,figsize=figsize)
    for i,y in enumerate(cols):
        for j,x in enumerate(cols):
            if i != n-1:
                ax[i,j].xaxis.set_ticklabels([])
            if j != 0:
                ax[i,j].yaxis.set_ticklabels([])
            if i != j:
                try:
                    tmp = df[[x,y]].copy()
                    tmp.dropna(inplace=True)
                    ax[i,j].plot(tmp[x].values,tmp[y].values,'.',markersize=0.5,alpha=0.5,color='black')
                except:
                    pass
            else:
                midx = df[x].min() + (df[x].max() - df[x].min())/2.0
                midy = df[y].min() + (df[y].max() - df[y].min())/2.0
                ax[i,j].text(midx, midy, y.replace(' ','\n'),
                    horizontalalignment='center',
                    verticalalignment='center')
            ax[i,j].set_ylim((df[y].min(),df[y].max()))
            ax[i,j].set_xlim((df[x].min(),df[x].max()))