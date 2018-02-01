import numpy as np
from noise import pnoise2, pnoise3
from scipy.ndimage.filters import gaussian_filter, gaussian_filter1d

def center_and_scale(drawing):
    """
    Translate an entire drawing to the mean location of the points,
    then scale the drawing to fit within +/-1.
    """
    all_points = np.vstack(drawing)
    meanxy = np.mean(all_points, axis=0)
    minxy = np.min(all_points, axis=0) - meanxy
    maxxy = np.max(all_points, axis=0) - meanxy
    max_range = np.max(np.abs((minxy, maxxy)))
    return [(stroke - meanxy) / max_range for stroke in drawing]

def get_noise_seed(seed=None):
    if seed is None:
        return np.random.rand(1) * 100000
    else:
        return seed
    
def noise_xy(points, scale=0.1, frequency=0.5, octaves=3, seed=None):
    """
    Generate a number of x,y points using Perlin noise.
    """
    seed = get_noise_seed(seed)
    tn = np.linspace(seed, seed + frequency, points)
    x = [pnoise2(0, float(t), octaves) * scale for t in tn]
    y = [pnoise2(1, float(t), octaves) * scale for t in tn]
    return x, y

def jitter_stroke(stroke, scale):
    """
    Jitter the points in a stroke with Perlin noise.
    """
    n = len(stroke)
    x, y = noise_xy(n, scale=scale)
    offsets = np.vstack([x, y])
    return stroke + offsets.T

def jitter(drawing, scale=0.1):
    """
    Jitter an entire drawing by jittering each stroke with Perlin noise.
    """
    return [jitter_stroke(stroke, scale) for stroke in drawing]

def warp_stroke(stroke, scale=0.5, frequency=0.5, octaves=3, seed=None):
    """
    Warp a stroke by applying a Perlin noise deformation field.
    """
    seed = get_noise_seed(seed)
    offsets = [[pnoise3(0 + seed, x, y, 3), pnoise3(1 + seed, x, y, 3)] for x, y in (stroke * frequency)]
    return stroke + np.asarray(offsets) * scale
    
def warp(drawing, scale=0.5, frequency=0.5, octaves=3, seed=None):
    """
    Warp a drawing by applying a Perlin noise deformation field.
    """
    seed = get_noise_seed(seed)
    return [warp_stroke(stroke, scale=scale, frequency=frequency, octaves=octaves, seed=seed) for stroke in drawing]

def smooth_position_stroke(stroke, sigma=1):
    """
    Smooth a stroke with a Gaussian filter.
    This smooths things in "sample space" rather than "real space".
    """
    stroke[:,0] = gaussian_filter1d(stroke[:,0], sigma=sigma, mode='nearest')
    stroke[:,1] = gaussian_filter1d(stroke[:,1], sigma=sigma, mode='nearest')
    return stroke
    
def smooth_position(drawing, sigma=1):
    """
    Smooth all the strokes in a drawing with a Gaussian filter.
    This smooths things in "sample space" rather than "real space".
    """
    sigma = np.abs(sigma * np.random.randn(1))
    return [smooth_position_stroke(stroke, sigma=sigma) for stroke in drawing]

def smooth_velocity_stroke(stroke, sigma=1):
    """
    Smooth a stroke by smoothing the derivative rather than the points directly.
    """
    x = stroke[:,0]
    y = stroke[:,1]
    xd = gaussian_filter1d(np.diff(x), sigma=sigma, mode='nearest')
    yd = gaussian_filter1d(np.diff(y), sigma=sigma, mode='nearest')
    stroke[1:,0] = x[0] + np.cumsum(xd)
    stroke[1:,1] = y[0] + np.cumsum(yd)
    return stroke
    
def smooth_velocity(drawing, sigma=1):
    """
    Smooth a drawing by smoothing the derivative rather than the points directly.
    """
    sigma = np.abs(sigma * np.random.randn(1))
    return [smooth_velocity_stroke(stroke, sigma=sigma) for stroke in drawing]

def jitter_scale(drawing, overall_sigma=0.1, aspect_sigma=0.05):
    """
    Scale an entire drawing about 0,0 by a random gaussian.
    """
    scale = (1 + np.random.randn(1) * overall_sigma) + np.random.randn(2) * aspect_sigma
    return [stroke * scale for stroke in drawing]

def jitter_translate(drawing, sigma=0.10):
    """
    Translate an entire drawing by a random gaussian.
    """
    translate = np.random.randn(2) * sigma
    return [stroke + translate for stroke in drawing]

def create_rotation_matrix(theta):
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[c, -s], [s, c]])

def jitter_rotate(drawing, sigma=0.2):
    """
    Rotate an entire drawing about 0,0 by a random gaussian.
    """
    rotation = np.random.randn(1) * sigma
    matrix = create_rotation_matrix(rotation)
    return [np.dot(stroke, matrix).squeeze() for stroke in drawing]

def jitter_translate_stroke(drawing, sigma=0.02):
    """
    Translate each stroke in a drawing by a random gaussian.
    """
    return [stroke + np.random.randn(2) * sigma for stroke in drawing]

def jitter_scale_stroke(drawing, sigma=0.05):
    """
    Scale each stroke in a drawing about the center of each stroke by a random gaussian.
    """
    centers = [np.mean(stroke) for stroke in drawing]
    return [((stroke - center) * (1 + np.random.randn(2) * sigma)) + center
            for center, stroke in zip(centers, drawing)]

def jitter_rotate_stroke(drawing, sigma=0.2):
    """
    Rotate each stroke in a drawing about the center of each stroke by a random gaussian.
    """
    rotation = np.random.randn(1) * sigma
    matrix = create_rotation_matrix(rotation)
    centers = [np.mean(stroke) for stroke in drawing]
    return [np.dot(stroke - center, matrix).squeeze() + center
            for center, stroke in zip(centers, drawing)]

def shuffle_strokes(drawing, amount=0.25):
    """
    Randomly swap the order of a percentage of the strokes in a drawing.
    May swap less than the given percentage if it undoes a previous swap.
    """
    n = len(drawing)
    stroke_indices = np.arange(n)
    shuffle_count = int(n * amount)
    for i in range(shuffle_count):
        i0 = np.random.randint(n)
        i1 = np.random.randint(n)
        temp = stroke_indices[i0]
        stroke_indices[i0] = stroke_indices[i1]
        stroke_indices[i1] = temp
    return [drawing[i] for i in stroke_indices]

def reverse_strokes(drawing, amount=0.25):
    """
    Randomly reverse the direction of a percentage of the strokes in a drawing.
    """
    n = len(drawing)
    indices = np.arange(n)
    np.random.shuffle(indices)
    flip_n = int(amount * n)
    flip_indices = indices[:flip_n]
    flips = [i in flip_indices for i in range(n)]
    return [np.flipud(stroke) if flip else stroke for flip, stroke in zip(flips, drawing)]