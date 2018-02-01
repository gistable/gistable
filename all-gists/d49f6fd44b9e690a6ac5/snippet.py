import sys, cv2

# Refactored https://realpython.com/blog/python/face-recognition-with-python/

def cascade_detect(cascade, image):
  gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
  return cascade.detectMultiScale(
    gray_image,
    scaleFactor = 1.15,
    minNeighbors = 5,
    minSize = (30, 30),
    flags = cv2.cv.CV_HAAR_SCALE_IMAGE
  )

def detections_draw(image, detections):
  for (x, y, w, h) in detections:
    print "({0}, {1}, {2}, {3})".format(x, y, w, h)
    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

def main(argv = None):
  if argv is None:
    argv = sys.argv

  cascade_path = sys.argv[1]
  image_path = sys.argv[2]
  result_path = sys.argv[3] if len(sys.argv) > 3 else None

  cascade = cv2.CascadeClassifier(cascade_path)
  image = cv2.imread(image_path)
  if image is None:
    print "ERROR: Image did not load."
    return 2

  detections = cascade_detect(cascade, image)
  detections_draw(image, detections)

  print "Found {0} objects!".format(len(detections))
  if result_path is None:
    cv2.imshow("Objects found", image)
    cv2.waitKey(0)
  else:
    cv2.imwrite(result_path, image)

if __name__ == "__main__":
  sys.exit(main())
