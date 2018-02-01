#!/usr/bin/env python
# Benchmark transferring data, part of troubleshooting https://github.com/tensorflow/tensorflow/issues/6116
#
# Take a independent workers communicating with b parameter shards
# Each worker tries to add to variables stored on parameter server as fast as
# possible.
# 
# macbook
# ps=1: 1.6 GB/s
# ps=2: 2.6 GB/s
# 
# xeon:
# ps=1: 0.5-0.6 GB/s
# ps=2: 1.1-1.3 GB/s
# ps=4: 1.7-1.9 GB/s
# ps=8: 2.6-3.1 GB/s
# ps=16: 2.3 GB/s
#
# There is significant slowdown when using larger sizes. For instance
# transferring 128MB chunks give about 446 MB/second. Changing to
# 1024MB chunks, the rate goes down to 102 MB/second
# 
# to run with tcmalloc, set
# export LD_PRELOAD="/usr/lib/libtcmalloc.so.4" 
#
# reduce spurious logging with TF_CPP_MIN_LOG_LEVEL=2
# Problems:
# - sometimes get scary message at the end, possibly because our ps worker
# quits while being connected to a session


import os
import subprocess
import sys
import tensorflow as tf
import threading
import time

flags = tf.flags
flags.DEFINE_integer("iters", 10, "Maximum number of additions")
flags.DEFINE_integer("data_mb", 128, "size of vector in MBs")
flags.DEFINE_integer("workers", 1, "number of workers")
flags.DEFINE_string("strategy", "push", "push to have workers update ps, pull "
                    "to have them pull data from ps, both to do both")
flags.DEFINE_integer("ps", 1, "number of ps shards")
flags.DEFINE_integer("starting_port", 12222, "first port to use")
flags.DEFINE_boolean("verbose", False, "extra logging")

# internal flags, don't use
flags.DEFINE_string("job_name", "", "worker or ps")
flags.DEFINE_integer("task_index", -1, "# of current task")
FLAGS = flags.FLAGS

session_config = tf.ConfigProto(intra_op_parallelism_threads=10,
                                inter_op_parallelism_threads=10)

# setup local cluster from flags
host = "127.0.0.1"
ps_ports = range(FLAGS.starting_port, FLAGS.starting_port+FLAGS.ps)
worker_ports = range(FLAGS.starting_port+FLAGS.ps, FLAGS.starting_port+FLAGS.ps+FLAGS.workers)

cluster = {"ps": [host+":"+str(p) for p in ps_ports],
           "worker": [host+":"+str(p) for p in worker_ports]}
clusterspec = tf.train.ClusterSpec(cluster).as_cluster_def()

dtype=tf.int32
params_size = 250*1000*FLAGS.data_mb # 1MB is 250k integers
sharded_params_size = params_size/FLAGS.ps

def log(s):
  if FLAGS.verbose:
    print(s)
    
def create_graph(worker):
  """Creates graph for worker worker and all ps shards"""
  
  params = []
  updates = []
  param_init_ops = []
  for i in range(FLAGS.ps):
    with tf.device("job:ps/task:"+str(i)):
      param = tf.get_variable(name="params"+str(i),
                              shape=[sharded_params_size],
                              dtype=dtype,
                              initializer=tf.zeros_initializer)
      params.append(param)
      param_init_ops.append(param.initializer)

  add_ops = []
  update_init_ops = []

  with tf.device("job:worker/task:"+str(worker)):
    for i in range(FLAGS.ps):
      update = tf.get_variable(name="update"+str(i),
                               shape=[sharded_params_size],
                               dtype=dtype,
                               initializer=tf.zeros_initializer)
      if FLAGS.strategy == "push":
        add_op = params[i].assign_add(update)
      elif FLAGS.strategy == "pull":
        add_op = update.assign_add(params[i])
      elif FLAGS.strategy == "both":
        local_update = tf.identity(params[i].read_value())
        add_op = params[i].assign_add(local_update)
      add_ops.append(add_op)
      update_init_ops.append(update.initializer)

  return update_init_ops, param_init_ops, add_ops

def create_done_queue(i):
  """Queue used to signal death for i'th ps shard. Intended to have 
  all workers enqueue an item onto it to signal doneness."""
  
  with tf.device("/job:ps/task:%d" % (i)):
    return tf.FIFOQueue(FLAGS.workers, tf.int32, shared_name="done_queue"+
                        str(i))
  
def create_done_queues():
  return [create_done_queue(i) for i in range(FLAGS.ps)]
    
def run_ps():
  """Main loop for single ps server shard. Initializes variables on that
  shard."""
  
  log("ps %d: running"%(FLAGS.task_index))

  server = tf.train.Server(cluster,
                           job_name=FLAGS.job_name,
                           task_index=FLAGS.task_index)
  sess = tf.Session(server.target, config=session_config)

  # run initialization for variables on this shard
  update_init_ops, param_init_ops, add_ops = create_graph(0)

  log("ps %d: initializing"%(FLAGS.task_index))
  sess.run(param_init_ops[FLAGS.task_index])
  
  queue = create_done_queue(FLAGS.task_index)
  
  # wait until all workers are done
  for i in range(FLAGS.workers):
    sess.run(queue.dequeue())
    log("ps %d received done %d" % (FLAGS.task_index, i))
  log("ps %d: quitting"%(FLAGS.task_index))

def run_worker():
  """Main loop for single worker."""
  
  log("worker %d: running"%(FLAGS.task_index))

  update_init_ops, param_init_ops, add_ops = create_graph(FLAGS.task_index)
  
  server = tf.train.Server(cluster,
                           job_name=FLAGS.job_name,
                           task_index=FLAGS.task_index)
  sess = tf.Session(server.target, config=session_config)
  sess.run(update_init_ops)

  # wait for parameter server variables to be initialized
  uninited_op = tf.report_uninitialized_variables()
  while(len(sess.run(uninited_op)) > 0):
    log("worker %d: ps uninitialized, sleeping" % FLAGS.task_index)
    time.sleep(1)
  
  for add_op in add_ops:
    sess.run(add_op.op)  # warm-up

  start_time = time.time()

  # communicate with parameter server in separate threads
  def create_worker_thread(add_op, iters):
    def worker_thread():
      for i in range(iters):
        sess.run(add_op.op)
    return worker_thread

  threads = []
  for i in range(FLAGS.ps):
    worker_thread_body = create_worker_thread(add_ops[i], FLAGS.iters)
    worker_thread = threading.Thread(target=worker_thread_body)
    worker_thread.start()
    threads.append(worker_thread)

  for thread in threads:
    thread.join()
      
  elapsed_time = time.time() - start_time
  rate = float(FLAGS.iters)*FLAGS.data_mb/elapsed_time
  print("worker %d done: %.2f MB per second" % (FLAGS.task_index, rate))

  # signal to ps shards that we are done
  for q in create_done_queues():
    sess.run(q.enqueue(1))
    
def launch_ps():
  for i in range(FLAGS.ps):
    cmd = "./" + " ".join(sys.argv) + " --job_name=ps --task="+str(i)
    my_env = os.environ.copy()
    my_env["CUDA_VISIBLE_DEVICES"] = ""
    subprocess.Popen(cmd, shell=True, stderr=subprocess.STDOUT,
                     env=my_env)
    
def launch_workers():
  for i in range(FLAGS.workers):
    cmd = "./" + " ".join(sys.argv) + " --job_name=worker --task="+str(i)
    my_env = os.environ.copy()
    # turn off GPU for speed
    my_env["CUDA_VISIBLE_DEVICES"] = ""
    subprocess.Popen(cmd, shell=True, stderr=subprocess.STDOUT,
                     env=my_env)
    
  
if __name__=='__main__':
  if FLAGS.job_name == "ps":
    run_ps()
  elif FLAGS.job_name == "worker":
    run_worker()
  else:
    log("client: launching ps")
    launch_ps()
    log("client: launching workers")
    launch_workers()
