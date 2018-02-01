# code from Stack Overflow with minor Python 3 tweaks
# Thanks to Andrew from SO for making such great code!
# http://stackoverflow.com/questions/14416130/dynamically-create-a-list-of-shared-arrays-using-python-multiprocessing
# For a reference on parallel processing in Python see this tutorial by David Beazley
# http://www.slideshare.net/dabeaz/an-introduction-to-python-concurrency
import time
import ctypes
import logging
try:
    import Queue
except ImportError:
    import queue as Queue
import multiprocessing as mp
import numpy as np

info = mp.get_logger().info


def main():
    logger = mp.log_to_stderr()
    logger.setLevel(logging.INFO)

    data_pipeline = Image_Data_Pipeline(
        num_data_buffers=5,
        buffer_shape=(60, 256, 512))
    start = time.clock()
    data_pipeline.load_buffers(data_pipeline.num_data_buffers)
    end = time.clock()
    data_pipeline.close()
    print("Elapsed time:", end-start)


class Image_Data_Pipeline:
    def __init__(self, num_data_buffers, buffer_shape):
        """
        Allocate a bunch of 16-bit buffers for image data
        """
        self.num_data_buffers = num_data_buffers
        self.buffer_shape = buffer_shape
        pix_per_buf = int(np.prod(buffer_shape))
        self.data_buffers = [mp.Array(ctypes.c_uint16, pix_per_buf)
                             for b in range(num_data_buffers)]
        self.idle_data_buffers = list(range(num_data_buffers))

        """
        Launch the child processes that make up the pipeline
        """
        self.camera = Data_Pipeline_Process(
            target=child_process, name='Camera',
            data_buffers=self.data_buffers, buffer_shape=buffer_shape)
        self.display_prep = Data_Pipeline_Process(
            target=child_process, name='Display Prep',
            data_buffers=self.data_buffers, buffer_shape=buffer_shape,
            input_queue=self.camera.output_queue)
        self.file_saving = Data_Pipeline_Process(
            target=child_process, name='File Saving',
            data_buffers=self.data_buffers, buffer_shape=buffer_shape,
            input_queue=self.display_prep.output_queue)
        return None

    def load_buffers(self, N, timeout=0):
        """
        Feed the pipe!
        """
        for i in range(N):
            self.camera.input_queue.put(self.idle_data_buffers.pop())

        """
        Wait for the buffers to idle. Here would be a fine place to
        feed them back to the pipeline, too.
        """
        while True:
            try:
                self.idle_data_buffers.append(
                    self.file_saving.output_queue.get_nowait())
                info("Buffer %i idle" % (self.idle_data_buffers[-1]))
            except Queue.Empty:
                time.sleep(0.01)
            if len(self.idle_data_buffers) >= self.num_data_buffers:
                break
        return None

    def close(self):
        self.camera.input_queue.put(None)
        self.display_prep.input_queue.put(None)
        self.file_saving.input_queue.put(None)
        self.camera.child.join()
        self.display_prep.child.join()
        self.file_saving.child.join()


class Data_Pipeline_Process:
    def __init__(self, target, name, data_buffers, buffer_shape,
                 input_queue=None, output_queue=None):
        if input_queue is None:
            self.input_queue = mp.Queue()
        else:
            self.input_queue = input_queue

        if output_queue is None:
            self.output_queue = mp.Queue()
        else:
            self.output_queue = output_queue

        self.command_pipe = mp.Pipe()  # For later, send instrument commands

        self.child = mp.Process(
            target=target,
            args=(name, data_buffers, buffer_shape,
                  self.input_queue, self.output_queue, self.command_pipe),
            name=name)
        self.child.start()
        return None


def child_process(name, data_buffers, buffer_shape, input_queue, output_queue,
                  command_pipe):
    if name == 'Display Prep':
        display_buffer = np.empty(buffer_shape, dtype=np.uint16)
    while True:
        try:
            process_me = input_queue.get_nowait()
        except Queue.Empty:
            time.sleep(0.01)
            continue
        if process_me is None:
            break  # We're done
        else:
            info("start buffer %i" % (process_me))
            with data_buffers[process_me].get_lock():
                a = np.frombuffer(data_buffers[process_me].get_obj(),
                                  dtype=np.uint16)
                if name == 'Camera':
                    """
                    Fill the buffer with data (eventually, from the
                    camera, dummy data for now)
                    """
                    a.fill(1)
                elif name == 'Display Prep':
                    """
                    Process the 16-bit image into a display-ready
                    8-bit image. Fow now, just copy the data to a
                    similar buffer.
                    """
                    display_buffer[:] = a.reshape(buffer_shape)
                elif name == 'File Saving':
                    """
                    Save the data to disk.
                    """
                    a.tofile('out.raw')
            info("end buffer %i" % (process_me))
            output_queue.put(process_me)
    return None

if __name__ == '__main__':
    main()