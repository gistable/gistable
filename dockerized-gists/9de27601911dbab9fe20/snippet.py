def build_startup(team, product, market, cash):
    while team and cash > 0:
        while not fits(product, market):
            apply_breadth_first_search()  # Apply with heuristics
        apply_depth_first_search()