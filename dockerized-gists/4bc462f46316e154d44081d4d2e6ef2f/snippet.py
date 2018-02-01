def joyplot(data, ax=None, 
            flatten = .1, #rescale the height of each distribution to avoid overlap. If large, will flatten out each of the KDEs
            linecolor='k', 
            shadecolor='w',
            alpha=1,
            shade=True, 
            line_kws = None,
            kde_kws=None,
            fig_kws=None,
            shade_kws=None):
    line_kws = dict() if line_kws is None else line_kws
    kde_kws = (dict(kernel='gau', bw='scott',
                         gridsize=100, cut=3,
                         clip=None) if kde_kws is None else kde_kws)
    fig_kws = dict(figsize=(5,5)) if fig_kws is None else fig_kws
    shade_kws = (dict(alpha=alpha, 
                          clip_on=True, 
                          color=shadecolor) if shade_kws is None else shade_kws)
    if kde_kws.get('clip',None) is None:
        kde_kws['clip'] = (-np.inf, np.inf)
    if ax is None:
        f,ax = plt.subplots(1,1, **fig_kws)
    T,N = data.shape
    dsupport = np.array([])
    max_zorder = 2*T
    zorder = max_zorder
    for i, row in enumerate(data):
        x,y = _statsmodels_univariate_kde(row, **kde_kws)
        y = np.max(np.c_[np.zeros_like(y), y], axis=1)
        y = y/(flatten*y.max()) + i
        ax.plot(x,y,color=linecolor, zorder=zorder, **line_kws)
        if shade:
            if shade_kws.get('color', None) is None:
                shade_kws['color'] = shadecolor
            ax.fill_between(x, i, y, zorder=zorder-1,
                             **shade_kws)
        dsupport = np.concatenate((dsupport, x))
        zorder -= 2
    ax.set_xlim(np.min(dsupport)*.75, np.max(dsupport)*1.25)
    return f,ax