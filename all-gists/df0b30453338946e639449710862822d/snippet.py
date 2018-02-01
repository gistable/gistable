import numpy as np
import pandas as pd
import pylab as pl
import os

from sklearn.neighbors import KNeighborsClassifier
from IPython.core.pylabtools import figsize
from PIL import Image

def load_image(filename):
    im = Image.open(filename)
    if im.mode is not 'RGBA':
        return im.convert(mode='RGBA')
    return im

def convert_to_dataframe(image):
    pixels = image.load()
    data = []
    all_colors = []
    for x in range(0, image.width):
        for y in range (0, image.height):
            pixel_color = rgba_to_hex(pixels[image.width - x - 1, image.height - y - 1])
            data.append([x, y, pixel_color])
            all_colors.append(pixel_color)
    return data, set(all_colors)

def rgba_to_hex(rgba_tuple):
    assert type(rgba_tuple) == tuple and len(rgba_tuple) == 4
    return "#{:02x}{:02x}{:02x}".format(rgba_tuple[0], rgba_tuple[1], rgba_tuple[2])

def save_to_file(filename, dataframes, size):
    ni = Image.new('RGBA', size, '#ff00ff')
    pixels = ni.load()
    for df in dataframes:
        for row in df.itertuples():
            pixels[size[0] - 1 - row.x, size[1] - 1 - row.y] = hex_to_rgba(row.color)
    ni.save(filename)

def hex_to_rgba(hex_string):
    return int(hex_string[1:3], 16), int(hex_string[3:5], 16), int(hex_string[5:7], 16), 255

def plot_k(data):
    accuracy = get_accuracy(data)
    results = pd.DataFrame(accuracy, columns=["n", "accuracy"])
    pl.plot(results.n, results.accuracy)
    pl.title("Accuracy for variable K")
    pl.show()

def get_accuracy(data):
    accuracy = []
    print "Plotting K..."
    is_missing = np.random.uniform(0, 1, len(data)) > 0.8
    train = data[is_missing == False]
    test = data[is_missing == True]
    for n in range(1, 20, 1):
        clf = KNeighborsClassifier(n_neighbors=n)
        clf.fit(train[['x', 'y']], train['color'])
        preds = clf.predict(test[['x', 'y']])
        k_accuracy = np.where(preds==test['color'], 1, 0).sum() / float(len(test))
        print "Neighbors: %d, Accuracy: %3f" % (n, k_accuracy)

        accuracy.append([n, k_accuracy])
    return accuracy

def run(image_name):
    im = load_image(image_name)
    filename, file_extension = os.path.splitext(image_name)
    data, all_cols = convert_to_dataframe(im)
    df = pd.DataFrame(data, columns=['x', 'y', 'color'])


    # generate missing data (in our case this is the same as our trainig/test sets)
    is_missing = np.random.uniform(0, 1, len(df)) > 0.7
    print "Total number of pixels:", len(df), "Pixels available:", np.where(is_missing==False)[0].size, "Pixels missing:", np.where(is_missing==True)[0].size
    train = df[is_missing==False]
    test = df[is_missing==True]
    save_to_file('{}_missing{}'.format(filename, file_extension), [train], (im.width, im.height))

    # Uncomment the following line to run the k-finding function
    # Caution: This will likely take a long time!
    # plot_k(train)

    clf = KNeighborsClassifier(n_neighbors=3)
    clf.fit(train[['x', 'y']], train['color'])

    save_to_file('{}_test{}'.format(filename, file_extension), [test], (im.width, im.height))
    preds = clf.predict(test[['x', 'y']])
    test.color = preds

    save_to_file('{}_predicted{}'.format(filename, file_extension), [test], (im.width, im.height))
    save_to_file('{}_combined{}'.format(filename, file_extension), [train, test], (im.width, im.height))

run('tree.png')