# Replace section 1.1 of Assignment 3 with the following lines of code
# Final result looks something like this: http://imgur.com/nVCFDPh

def pts_set_2():

  def create_intermediate_points(pt1, pt2, granularity):
    new_pts = []
    vector = np.array([(x[0] - x[1]) for x in zip(pt1, pt2)])
    return [(np.array(pt2) + (vector * (float(i)/granularity))) for i in range(1, granularity)]

  pts = []
  granularity = 20

  # Create cube wireframe
  pts.extend([[-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1], \
              [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]])

  pts.extend(create_intermediate_points([-1, -1, 1], [1, -1, 1], granularity))
  pts.extend(create_intermediate_points([1, -1, 1], [1, 1, 1], granularity))
  pts.extend(create_intermediate_points([1, 1, 1], [-1, 1, 1], granularity))
  pts.extend(create_intermediate_points([-1, 1, 1], [-1, -1, 1], granularity))

  pts.extend(create_intermediate_points([-1, -1, -1], [1, -1, -1], granularity))
  pts.extend(create_intermediate_points([1, -1, -1], [1, 1, -1], granularity))
  pts.extend(create_intermediate_points([1, 1, -1], [-1, 1, -1], granularity))
  pts.extend(create_intermediate_points([-1, 1, -1], [-1, -1, -1], granularity))

  pts.extend(create_intermediate_points([1, 1, 1], [1, 1, -1], granularity))
  pts.extend(create_intermediate_points([1, -1, 1], [1, -1, -1], granularity))
  pts.extend(create_intermediate_points([-1, -1, 1], [-1, -1, -1], granularity))
  pts.extend(create_intermediate_points([-1, 1, 1], [-1, 1, -1], granularity))

  # Create triangle wireframe
  pts.extend([[-0.5, -0.5, -1], [0.5, -0.5, -1], [0, 0.5, -1]])
  pts.extend(create_intermediate_points([-0.5, -0.5, -1], [0.5, -0.5, -1], granularity))
  pts.extend(create_intermediate_points([0.5, -0.5, -1], [0, 0.5, -1], granularity))
  pts.extend(create_intermediate_points([0, 0.5, -1], [-0.5, -0.5, -1], granularity))

  return np.array(pts)

pts = pts_set_2()