import numpy as np

rawpoints = np.array(
   [[2500, 0.15, 12],
    [1200, 0.65, 20],
    [6200, 0.35, 19]]
) 

# Scale the rawpoints array so that each "column" is
# normalized to the same scale
# Linear stretch from lowest value = 0 to highest value = 100
high = 100.0
low = 0.0

mins = np.min(rawpoints, axis=0)
maxs = np.max(rawpoints, axis=0)
rng = maxs - mins

scaled_points = high - (((high - low) * (maxs - rawpoints)) / rng)

"""
scaled points ->
   [[  26.,     0.,     0., ],
    [   0.,   100.,   100., ],
    [ 100.,    40.,    87.5,]]
"""
