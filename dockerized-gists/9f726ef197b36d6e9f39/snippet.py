def varianceSelection(X, THRESHOLD = .95):
    sel = VarianceThreshold(threshold=(THRESHOLD * (1 - THRESHOLD)))
    sel.fit_transform(X)
    return X[[c for (s, c) in zip(sel.get_support(), X.columns.values) if s]]
