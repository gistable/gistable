########
# This code creates 2 sub-processes: one that continually polls a webcam and labels each resulting image with a timestamp, and another that saves these images to file. The process that saves the images to file doesn't save all the images, but instead listens to the main process for time windows that it should save. This permits one to save only certain time windows (toss images that fall outside this time window) and avoids the capture start up lag that occurs if you simply try to poll the webcam during the time window of interest (this lag can be several tenths of a second!). Converting the images to string then pickling before queueing them was necessary because opencv's iplimage format doesn't like to be put in a queue directly.
########

import multiprocessing
import cv
import cPickle
import time

queue_to_cam_writer = multiprocessing.Queue()
queue_from_cam_writer = multiprocessing.Queue()

queue_to_cam_capture = multiprocessing.Queue()
queue_from_cam_capture = multiprocessing.Queue()

def cam_writer_loop(queue_to_cam_writer,queue_from_cam_writer,queue_from_cam_capture):
	done = False
	start_list = []
	stop_list = []
	trial_list = []
	i = 0
	while not done:
		if not queue_to_cam_writer.empty():
			from_queue = queue_to_cam_writer.get()
			if from_queue=='quit':
				done = True
			elif from_queue[0]=='start':
				start_list.append(from_queue[1])
				stop_list.append(999999999999)
				trial_list.append(from_queue[2])
			elif from_queue[0]=='stop':
				stop_list[-1] = from_queue[1]
		if not queue_from_cam_capture.empty():
			from_queue = queue_from_cam_capture.get()
			if len(start_list)>0:
				t = from_queue[0]
				if t>start_list[0]:
					if t>stop_list[0]:
						queue_from_cam_writer.put(['done',trial_list[0]])
						del(start_list[0])
						del(stop_list[0])
						del(trial_list[0])
						i = 0
					else:
						i = i + 1
						image_as_pickled_string = from_queue[1]
						image_size = from_queue[2]
						image_as_string = cPickle.loads(image_as_pickled_string)
						image = cv.CreateImageHeader(image_size, cv.IPL_DEPTH_8U, 3)
						cv.SetData(image, image_as_string)
						cv.SaveImage('./temp/'+str(trial_list[0])+'_'+str(i)+'_'+str(t-start_list[0])+'.png',image)


cam_writer_process = multiprocessing.Process(target=cam_writer_loop,args=(queue_to_cam_writer,queue_from_cam_writer,queue_from_cam_capture,))
cam_writer_process.start()


def cam_capture_loop(queue_to_cam_capture,queue_from_cam_capture):
	cam = cv.CaptureFromCAM(-1)
	done = False
	i = 0
	start = time.time()
	while not done:
		if not queue_to_cam_capture.empty():
			from_queue = queue_to_cam_capture.get()
			if from_queue=='quit':
				done = True
		image = cv.QueryFrame(cam)
		t = time.time()
		image_as_string = image.tostring()
		image_as_pickled_string = cPickle.dumps(image_as_string,-1)
		queue_from_cam_capture.put([t,image_as_pickled_string,cv.GetSize(image)])
		i = i + 1
		time.sleep(0.001) #neccessary to give the cam_writer_process time to unqueue and thereby avoid a memory overflow
	print [i*1.0/(t-start)]
	del(cam)


cam_capture_process = multiprocessing.Process(target=cam_capture_loop,args=(queue_to_cam_capture,queue_from_cam_capture,))
cam_capture_process.start()

time.sleep(5)
print 'starting'
queue_to_cam_writer.put(['start',time.time(),1])
time.sleep(1)
print 'stopping'
queue_to_cam_writer.put(['stop',time.time()])

time.sleep(5)
print 'starting'
queue_to_cam_writer.put(['start',time.time(),2])
time.sleep(1)
print 'stopping'
queue_to_cam_writer.put(['stop',time.time()])


print 'waiting for writer to finish'
done = False
while not done:
	if not queue_from_cam_writer.empty():
		from_queue = queue_from_cam_writer.get()
		if from_queue[0]=='done':
			if from_queue[1]==2:
				done = True

print 'quitting'
queue_to_cam_writer.put('quit')
queue_to_cam_capture.put('quit')

print 'joining writer'
cam_writer_process.join()
print 'killing writer'
cam_writer_process.terminate()

print 'killing capture'
cam_capture_process.terminate()

print 'done'
