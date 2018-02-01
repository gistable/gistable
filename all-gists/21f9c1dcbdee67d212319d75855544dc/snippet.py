'''
Post: http://gciruelos.com/what-is-the-roundest-country.html
Compute and create table of the roundness of all the countries.
Needs file ne_10m_admin_0_sovereignty.
'''

import base64
import io
import math
import operator
import random
import time
import urllib

import matplotlib.pyplot as plt
from PIL import Image
import rtree
import shapefile
from shapely.geometry import Polygon, Point
import pyproj

def slice_at(plist, indices):
    '''
    Slices the list ll at the indices indicated.
    '''
    indices.append(len(plist))
    for fro, to in zip(indices, indices[1:]):
        yield plist[fro:to]

def plot_country(name, parts, center, radius):
    fig, ax = plt.subplots(figsize=(1.8, 1.8))

    circle = plt.Circle(center, radius, color='k', fill=False)
    for part in parts:
        #color = random.choice('bgrcmk')
        color = 'k'
        for point1, point2 in zip(part, part[1:]):
            ax.plot(
                [point1[0], point2[0]],
                [point1[1], point2[1]],
                color+'-')
    ax.add_artist(circle)
    ax.set_aspect('equal', 'datalim')
    imgdata = io.BytesIO()
    #ax.set_title(name)
    plt.axis('off')
    #plt.savefig(name.lower().replace(' ', '-') + '.png', transparent=True)
    #plt.show()
    plt.savefig('tmp.png', format='png', transparent=True)
    img = Image.open('tmp.png')
    png_info = img.info
    img.convert('P').save(imgdata, 'PNG', **png_info)
    imgdata.seek(0)
    plt.close(fig)
    return imgdata

def neighbours(center, radius, delta):
    cmov = delta
    rmov = delta
    cms = [cmov*20, cmov, 0, -cmov, -cmov*20]
    rms = [rmov*20, rmov, 0, -rmov, -rmov*20]
    for cx_mov in cms:
        for cy_mov in cms:
            for r_mov in rms:
                if radius + r_mov > 0:
                    yield ((center[0] + cx_mov, center[1] + cy_mov),
                           radius + r_mov)

def maxmin(arr):
    _max = arr[0]
    _min = arr[0]
    for x in arr:
        if x > _max:
            _max = x
        elif x < _min:
            _min = x
    return _max, _min

def heuristic(polygons, index, c, r, delta, iters=200):
    best_coeff = 0
    parts_area = sum(map(lambda x: x.area, polygons))
    is_ = 0
    for _ in range(iters):
        is_ += 1
        mejoro = False
        for c_, r_ in neighbours(c, r, delta):
            circle = Point(c_).buffer(r_)
            indices = range(len(polygons))
            if circle.bounds != ():
                indices = [int(i) for i in index.intersection(circle.bounds)]
            else:
                print('WARNING: circle.bounds == (). '\
                      'center = %s, radius = %.3f' % (str(c_), r_))
            intersection_area = sum(
                [polygons[i].intersection(circle).area for i in indices])
            coeff = intersection_area / max(math.pi * r_ * r_, parts_area)
            #print(c_, r_)
            #print(intersection_area, circle_area, parts_area)
            if coeff > best_coeff:
                mejoro = True
                c = c_
                r = r_
                best_coeff = coeff
        if not mejoro:
            break
    return c, r, best_coeff, is_

def circle_inside(xmin, ymin, xmax, ymax):
    center = [(xmin + xmax) / 2, (ymin + ymax) / 2]
    radius = min((xmax - xmin) / 2, (ymax - ymin) / 2)
    return center, radius

def circle_outside(xmin, ymin, xmax, ymax):
    center = [(xmin + xmax) / 2, (ymin + ymax) / 2]
    radius = math.sqrt((xmax - xmin)**2.0 + (ymax - ymin)**2.0) / 2
    return center, radius

def analyze_both_circles(polys, index, min_x, min_y, max_x, max_y):
    cinside, rinside = circle_inside(min_x, min_y, max_x, max_y)
    coutside, routside = circle_outside(min_x, min_y, max_x, max_y)
    c_i, r_i, best_i, iin = heuristic(
        polys, index, cinside, rinside, rinside / 200)
    print('[%d, ' % iin, end='', flush=True)
    c_o, r_o, best_o, iout = heuristic(
        polys, index, coutside, routside, routside / 200)
    print('%d]' % iout)
    best_coeff_ = max(best_i, best_o)
    center_ = c_i if best_i > best_o else c_o
    radius_ = r_i if best_i > best_o else r_o
    return center_, radius_, best_coeff_

def find_best_circle(parts, minx, miny, maxx, maxy):
    polys = [Polygon(part).buffer(0) for part in parts]
    index = rtree.index.Index()
    for i, poly in enumerate(polys):
        index.insert(i, poly.bounds)
    print('Analyzing best overall circle...  Iterations: ', end='', flush=True)
    c, r, best_coeff = analyze_both_circles(
        polys, index, minx, miny, maxx, maxy)
    best_polygons = []
    if len(polys) > 1:
        polygons_area = sorted(
            [(poly, poly.area) for poly in polys],
            key=lambda x: x[1], reverse=True)
        areas = list(map(lambda r: r[1], polygons_area))
        if areas[0] > sum(areas[1:]):
            best_polygons = [polygons_area[0][0]]
        else:
            best_polygons = list(map(lambda x: x[0], polygons_area))[:5]
    i = 0
    for part in best_polygons:
        if len(polys) == 1:
            break
        i += 1
        print('Analyzing best part circle... (%d out of %d) Iterations: ' \
            % (i, len(polys)), end='', flush=True)
        x, y = part.exterior.coords.xy
        max_x, min_x = maxmin(x)
        max_y, min_y = maxmin(y)
        center_, radius_, best_coeff_ = analyze_both_circles(
            polys, index, min_x, min_y, max_x, max_y)
        if best_coeff_ > best_coeff:
            c = center_
            r = radius_
            best_coeff = best_coeff_
    # fine tune it.
    print('Fine-tuning the circle... Iterations: ', end='', flush=True)
    c, r, best_coeff, iters = heuristic(polys, index, c, r, r / 1000, 1000)
    print('[%d]' % iters)
    return c, r, best_coeff

def tuple2list(t):
    t = tuple(t)[0]
    return [t[0], t[1]]

def concat(ls):
    return [j for i in ls for j in i]

def mean(ls):
    return float(sum(ls)) / len(ls)

INPUT_FILE = 'ne_10m_admin_0_sovereignty'
FROM_PROJ = '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'

def main():
    countries = shapefile.Reader(INPUT_FILE).shapeRecords()
    results = {}

    for country in countries:
        t0 = time.process_time()
        name = country.record[8]
        # if name != 'Nauru': continue
        print('==== %s (%d -> %d) ====' % (
            name, len(country.shape.parts), len(country.shape.points)))
        points = list(map(lambda x: x, country.shape.points))

        parts_ = list(country.shape.parts) + [len(country.shape.points)]
        largest_part = (0, 1)
        for x1, x2 in zip(parts_, parts_[1:]):
            if x2 - x1 > largest_part[1] - largest_part[0]:
                largest_part = (x1, x2)
        print(parts_, largest_part)

        # Get the random points from the largest part.
        random_points = list(
            map(
                list,
                random.sample(points[largest_part[0]:largest_part[1]], 2)))

        # Get the middle points between them.
        lon, lat = list(
            pyproj.Geod(ellps='WGS84').npts(
                random_points[0][0], random_points[0][1],
                random_points[1][0], random_points[1][1],
                1)  # Just 1 point in-between them.
            )[0]

        to_proj = '+proj=aeqd +R=6371000 +lat_0=%.2f +lon_0=%.2f ' \
                  '+no_defs' % (lat, lon)
        print('Projection: %s' % to_proj)

        transform = lambda g: pyproj.transform(
            pyproj.Proj(FROM_PROJ),
            pyproj.Proj(to_proj),
            g[0], g[1])
        points = list(map(transform, points))

        parts = list(slice_at(points, country.shape.parts))
        max_xs, min_xs = maxmin(list(map(lambda t: t[0], points)))
        max_ys, min_ys = maxmin(list(map(lambda t: t[1], points)))

        center, radius, best_coeff = find_best_circle(
            parts, min_xs, min_ys, max_xs, max_ys)

        print('Time to compute roundness: %.3fs.' % (time.process_time() - t0))
        print('Result info: %f (%.4f, %.4f) %.4f' \
            % (best_coeff, center[0], center[1], radius))
        uri = 'data:image/png;base64,' + urllib.parse.quote(
            base64.b64encode(
                plot_country(name, parts, center, radius).getvalue()))
        print('Finished plotting %s.' % name)
        results[name] = (best_coeff, '<img src="%s" />' % uri)

    f = open('table', 'w')
    # Does python use theorems for free?
    # (https://www.mpi-sws.org/~dreyer/tor/papers/wadler.pdf)
    f.write(
        '\n'.join(
            map(lambda s: ' | '.join(map(str, s)),
                map(lambda r: [r[0]+1, r[1][0],
                               '%.3f' % r[1][1][0],
                               r[1][1][1]],
                    enumerate(
                        sorted(results.items(),
                               key=lambda z: (operator.itemgetter(1)(z))[0],
                               reverse=True))))))
    f.close()

#cProfile.run('main()')
main()