"""
The Bresenham Algorithm creates a list of cells/pixels that a straight
line intersects in a grid/raster/bitmap.

This example script gives the Bresenham Algorithm in 2D and 3D.
"""


def main():
    points_2d = bresenham_line_2d(0, 0, 6, 2)
    print(points_2d)

    points_3d = bresenham_line_3d((0, 0, 0), (6, 2, 2))
    print(points_3d)


def bresenham_line_2d(x0, y0, x1, y1):
    "Bresenham's line algorithm"
    points = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    x, y = x0, y0
    sx = -1 if x0 > x1 else 1
    sy = -1 if y0 > y1 else 1

    if dx > dy:
        err = dx / 2.0
        while x != x1:
            points.append((x, y))
            err -= dy
            if err < 0:
                y += sy
                err += dx
            x += sx
    else:
        err = dy / 2.0
        while y != y1:
            points.append((x, y))
            err -= dx
            if err < 0:
                x += sx
                err += dy
            y += sy

    points.append((x1, y1))

    return points


def bresenham_line_3d(p1, p2):
    "Bresenham's line algorithm"
    points = []
    z0, x0, y0 = tuple(p1)
    z1, x1, y1 = tuple(p2)
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    dz = abs(z1 - z0)
    z, x, y = z0, x0, y0
    sx = -1 if x0 > x1 else 1
    sy = -1 if y0 > y1 else 1
    sz = -1 if z0 > z1 else 1

    if dz > dx and dz > dy:
        err_x = dz / 2.0
        err_y = dz / 2.0
        while z != z1:
            points.append((z, x, y))
            err_x -= dx
            if err_x < 0:
                x += sx
                err_x += dz
            err_y -= dy
            if err_y < 0:
                y += sy
                err_y += dz
            z += sz
    elif dx > dy:
        err_z = dx / 2.0
        err_y = dx / 2.0
        while x != x1:
            points.append((z, x, y))
            err_y -= dy
            if err_y < 0:
                y += sy
                err_y += dx
            err_z -= dz
            if err_z < 0:
                z += sz
                err_z += dx
            x += sx
    else:
        err_x = dy / 2.0
        err_z = dy / 2.0
        while y != y1:
            points.append((z, x, y))
            err_x -= dx
            if err_x < 0:
                x += sx
                err_x += dy
            err_z -= dz
            if err_z < 0:
                z += sz
                err_z +=  dy
            y += sy

    points.append(p2)

    return points


if __name__ == '__main__':
    main()
