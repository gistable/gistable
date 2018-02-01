# -*- coding: utf-8 -*-
import numpy as np
import xml.etree.ElementTree as ET
from pycocotools.coco import COCO


def convert_coco_bbox(size, box):
    dw = 1. / size[0]
    dh = 1. / size[1]
    x = box[0] + box[2] / 2.0
    y = box[1] + box[3] / 2.0
    w = box[2]
    h = box[3]
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return x, y, w, h


def convert_bbox(size, box):
    dw = 1. / size[0]
    dh = 1. / size[1]
    x = (box[0] + box[1]) / 2.0
    y = (box[2] + box[3]) / 2.0
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return x, y, w, h


def area(x):
    if len(x.shape) == 1:
        return x[0] * x[1]
    else:
        return x[:, 0] * x[:, 1]


def kmeans_iou(k, centroids, points, iter_count=0, iteration_cutoff=25, feature_size=13):

    best_clusters = []
    best_avg_iou = 0
    best_avg_iou_iteration = 0

    npoi = points.shape[0]
    area_p = area(points)  # (npoi, 2) -> (npoi,)

    while True:
        cen2 = centroids.repeat(npoi, axis=0).reshape(k, npoi, 2)
        cdiff = points - cen2
        cidx = np.where(cdiff < 0)
        cen2[cidx] = points[cidx[1], cidx[2]]

        wh = cen2.prod(axis=2).T  # (k, npoi, 2) -> (npoi, k)
        dist = 1. - (wh / (area_p[:, np.newaxis] + area(centroids) - wh))  # -> (npoi, k)
        belongs_to_cluster = np.argmin(dist, axis=1)  # (npoi, k) -> (npoi,)
        clusters_niou = np.min(dist, axis=1)  # (npoi, k) -> (npoi,)
        clusters = [points[belongs_to_cluster == i] for i in range(k)]
        avg_iou = np.mean(1. - clusters_niou)
        if avg_iou > best_avg_iou:
            best_avg_iou = avg_iou
            best_clusters = clusters
            best_avg_iou_iteration = iter_count

        print("\nIteration {}".format(iter_count))
        print("Average iou to closest centroid = {}".format(avg_iou))
        print("Sum of all distances (cost) = {}".format(np.sum(clusters_niou)))

        new_centroids = np.array([np.mean(c, axis=0) for c in clusters])
        isect = np.prod(np.min(np.asarray([centroids, new_centroids]), axis=0), axis=1)
        aa1 = np.prod(centroids, axis=1)
        aa2 = np.prod(new_centroids, axis=1)
        shifts = 1 - isect / (aa1 + aa2 - isect)

        # for i, s in enumerate(shifts):
        #     print("{}: Cluster size: {}, Centroid distance shift: {}".format(i, len(clusters[i]), s))

        if sum(shifts) == 0 or iter_count >= best_avg_iou_iteration + iteration_cutoff:
            break

        centroids = new_centroids
        iter_count += 1

    # Get anchor boxes from best clusters
    anchors = np.asarray([np.mean(cluster, axis=0) for cluster in best_clusters])
    anchors = anchors[anchors[:, 0].argsort()]
    print("k-means clustering pascal anchor points (original coordinates) \
    \nFound at iteration {} with best average IoU: {} \
    \n{}".format(best_avg_iou_iteration, best_avg_iou, anchors*feature_size))

    return anchors


def load_pascal_dataset(datasets):
    name = 'pascal'
    data = []

    for year, image_set in datasets:
        img_ids_filename = '%s/%s/VOCdevkit/VOC%s/ImageSets/Main/%s.txt' % (source_dir, name, year, image_set)
        ifs_img_ids = open(img_ids_filename)
        img_ids = ifs_img_ids.read().strip().split()

        for image_id in img_ids:
            anno_filename = '%s/%s/VOCdevkit/VOC%s/Annotations/%s.xml' % (source_dir, name, year, image_id)
            ifs_anno = open(anno_filename)
            tree = ET.parse(ifs_anno)
            root = tree.getroot()
            size = root.find('size')
            w = int(size.find('width').text)
            h = int(size.find('height').text)

            for obj in root.iter('object'):
                xmlbox = obj.find('bndbox')
                b = (float(xmlbox.find('xmin').text),
                     float(xmlbox.find('xmax').text),
                     float(xmlbox.find('ymin').text),
                     float(xmlbox.find('ymax').text))
                bb = convert_bbox((w, h), b)
                data.append(bb[2:])

            ifs_anno.close()
        ifs_img_ids.close()

    return np.array(data)


def load_coco_dataset(datasets):
    name = 'coco'
    data = []

    for dataset in datasets:
        annfile = '%s/%s/annotations/instances_%s.json' % (source_dir, name, dataset)
        coco = COCO(annfile)
        cats = coco.loadCats(coco.getCatIds())
        base_classes = {cat['id']: cat['name'] for cat in cats}
        img_id_set = set()

        for cat_ids in base_classes.iterkeys():
            img_ids = coco.getImgIds(catIds=cat_ids)
            img_id_set = img_id_set.union(set(img_ids))
        image_ids = list(img_id_set)

        for image_id in image_ids:
            annIds = coco.getAnnIds(imgIds=image_id)
            anns = coco.loadAnns(annIds)
            img = coco.loadImgs(image_id)[0]
            w = img['width']
            h = img['height']

            for ann in anns:
                b = ann['bbox']
                bb = convert_coco_bbox((w, h), b)
                data.append(bb[2:])

    return np.array(data)

if __name__ == "__main__":

    # examples
    # k, pascal, coco
    # 1, 0.30933335617, 0.252004954777
    # 2, 0.45787906725, 0.365835079771
    # 3, 0.53198291772, 0.453180358467
    # 4, 0.57562962803, 0.500282182136
    # 5, 0.58694643198, 0.522010174068
    # 6, 0.61789602056, 0.549904351137
    # 7, 0.63443906479, 0.569485509501
    # 8, 0.65114747974, 0.585718648162
    # 9, 0.66393113546, 0.601564171461

    # k-means picking the first k points as centroids
    img_size = 416
    k = 5

    # change this line to match your system.
    source_dir = "/media/RED6/DATA"

    random_data = np.random.random((1000, 2))
    centroids = np.random.random((k, 2))
    random_anchors = kmeans_iou(k, centroids, random_data)

    subsets = (('2007', 'train'), ('2007', 'val'), ('2012', 'train'), ('2012', 'val'))
    pascal_data = load_pascal_dataset(subsets)
    centroids = pascal_data[np.random.choice(np.arange(len(pascal_data)), k, replace=False)]
    # centroids = pascal_data[:k]
    pascal_anchors = kmeans_iou(k, centroids, pascal_data, feature_size=img_size / 32)

    subsets = ('train2014', 'val2014')
    # subsets = ('test2014', 'test2015')
    coco_data = load_coco_dataset(subsets)
    centroids = coco_data[np.random.choice(np.arange(len(coco_data)), k, replace=False)]
    # centroids = coco_data[:k]
    coco_anchors = kmeans_iou(k, centroids, coco_data, feature_size=img_size / 32)

    print 'done'
