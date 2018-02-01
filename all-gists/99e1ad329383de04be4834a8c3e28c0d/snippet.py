import sys
import os
import cv2
import numpy as np
import tensorflow as tf

sys.path.append("..")

from object_detection.utils import label_map_util

MODEL_NAME = 'ssd_mobilenet_v1_coco_11_06_2017'
MODEL_FILE = MODEL_NAME + '.tar.gz'
DOWNLOAD_BASE = 'http://download.tensorflow.org/models/object_detection/'
PATH_TO_CKPT = MODEL_NAME + '/frozen_inference_graph.pb'
PATH_TO_LABELS = os.path.join('data', 'mscoco_label_map.pbtxt')
NUM_CLASSES = 90

label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES,
                                                            use_display_name=True)
category_index = label_map_util.create_category_index(categories)

def detect_alert(boxes, classes, scores, category_index, max_boxes_to_draw=20,
                 min_score_thresh=.5,
                 ):
    r = []
    for i in range(min(max_boxes_to_draw, boxes.shape[0])):
        if scores is None or scores[i] > min_score_thresh:
            test1 = None
            test2 = None

            if category_index[classes[i]]['name']:
                test1 = category_index[classes[i]]['name']
                test2 = int(100 * scores[i])

            line = {}
            line[test1] = test2
            r.append(line)

    return r

def detect_objects(image_np, sess, detection_graph):
    image_np_expanded = np.expand_dims(image_np, axis=0)
    image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
    boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
    scores = detection_graph.get_tensor_by_name('detection_scores:0')
    classes = detection_graph.get_tensor_by_name('detection_classes:0')
    num_detections = detection_graph.get_tensor_by_name('num_detections:0')

    # Actual detection.
    (boxes, scores, classes, num_detections) = sess.run(
        [boxes, scores, classes, num_detections],
        feed_dict={image_tensor: image_np_expanded})

    alert_array = detect_alert(np.squeeze(boxes), np.squeeze(classes).astype(np.int32), np.squeeze(scores),
                               category_index)
    return alert_array

IMAGE_SIZE = (12, 8)

def load_image_into_numpy_array(image):
    (im_width, im_height) = image.size
    return np.array(image.getdata()).reshape(
        (im_height, im_width, 3)).astype(np.uint8)

detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

def process_image(image):
    with detection_graph.as_default():
        with tf.Session(graph=detection_graph) as sess:
            alert_array = detect_objects(image, sess, detection_graph)

            alert = False

            for q in alert_array:
                print (q)
                if 'donut' in q:
                    if q['donut'] > 87: #manual rule example
                        alert = True

            return alert

video = cv2.VideoCapture('demo_8_1.mp4') #change the path of the video
success, image = video.read()
count = 0
success = True
while success:
    success, image = video.read()
    print 'Read a new frame: ', success
    if success:
        img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        alert = process_image(img)
        if alert:
            break
    count += 1