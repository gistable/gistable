"""Example of barrier implementation using TensorFlow shared variables.

All workers synchronize on barrier, copy global parameters to local versions
and increment global parameter variable asynchronously. Should see something
like this:

bash> killall python
bash> python simple_barrier.py --num_workers=4
worker  0, local_param  4 global_param  5
worker  2, local_param  4 global_param  7
worker  1, local_param  4 global_param  7
worker  3, local_param  4 global_param  8
worker  3, local_param  8 global_param 10
worker  2, local_param  8 global_param 11
"""

import numpy as np
import subprocess
import sys
import tensorflow as tf
import threading
import time

flags = tf.flags
flags.DEFINE_integer("iters", 10, "Maximum number of steps")
flags.DEFINE_integer("starting_port", "12222", "port of first worker")
flags.DEFINE_integer("num_workers", 4, "number of workers")
flags.DEFINE_integer("task", -1, "internal use")
flags.DEFINE_float("sleep_interval", 0.1, "how long to sleep in wait loop")
FLAGS = flags.FLAGS

# setup local cluster from flags
host = "127.0.0.1:"
s = FLAGS.starting_port
N = FLAGS.num_workers
cluster = {"worker": [host+str(port) for port in range(s, s+N)]}
clusterspec = tf.train.ClusterSpec(cluster).as_cluster_def()

# global ops
init_op = None
train_ops = []       # worker local train ops, read local params, update global
counter_vars = []    # counters for barrier
counter_adder_ops = []
global_param_var = None
local_param_vars = []
local_param_sync_ops = []

def default_config():
  optimizer_options = tf.OptimizerOptions(opt_level=tf.OptimizerOptions.L0)
  config = tf.ConfigProto(
    graph_options=tf.GraphOptions(optimizer_options=optimizer_options))
  config.log_device_placement = False
  config.allow_soft_placement = False
  return config

def create_graph(devices):
  """Create graph that keeps global params + counters on devices[0] and
  local params/train ops on devices[:]"""

  global train_ops, counter_vars, counter_adder_ops, global_param_var, local_param_vars, local_param_sync_ops

  dtype=tf.int32

  with tf.device(devices[0]):
    global_param_var = tf.get_variable("param", shape=(), dtype=dtype,
                                       initializer=tf.zeros_initializer)
    for i in range(2):
      counter_var = tf.get_variable("counter-"+str(i), (), tf.int32,
                                    initializer=tf.zeros_initializer)
      counter_vars.append(counter_var)
      counter_adder_ops.append(counter_var.assign_add(1, use_locking=True))

  # create local version of parameters
  for (i, device) in enumerate(devices):
    with tf.device(device):
      local_param_var = tf.get_variable("local_param-"+str(i), (), dtype,
                                        initializer=tf.zeros_initializer)
      local_param_vars.append(local_param_var)
      
      local_param_sync_op = local_param_var.assign(global_param_var)
      local_param_sync_ops.append(local_param_sync_op)
      train_op = global_param_var.assign_add(1)
      train_ops.append(train_op)

      
  init_op = tf.initialize_all_variables()
  return (init_op, train_ops)


def create_worker_threads(sess):
  """Creates a thread for each op in ops, running it iters times."""

  def barrier():
    sess.run(counter_adder_ops[0])
    while sess.run(counter_vars[0]) % N != 0:
      time.sleep(FLAGS.sleep_interval)
    sess.run(counter_adder_ops[1])
    while sess.run(counter_vars[1]) % N != 0:
      time.sleep(FLAGS.sleep_interval)
    
  def create_run_method(worker_id):
    def _run():
      local_param_var = local_param_vars[worker_id]
      sync_op = local_param_sync_ops[worker_id]
      train_op = train_ops[worker_id]
      for i in range(FLAGS.iters):
        barrier()
        sess.run(sync_op)
        barrier()
        old_val, updated_val = sess.run([local_param_var, train_op])
        print("worker %2d, local_param %2d global_param %2d" %(worker_id,
                                                               old_val,
                                                               updated_val))
    return _run

  return [threading.Thread(target=create_run_method(i))
          for i in range(N)]


def wait_for_threads_to_finish(threads):
  while any(t.is_alive() for t in threads):
    time.sleep(FLAGS.sleep_interval)


def launch_workers():
  """Launch processes running TensorFlow servers."""
  
  def runcmd(cmd): subprocess.Popen(cmd, shell=True, stderr=subprocess.STDOUT)
  for i in range(N):
    cmd = "python simple_barrier.py --task="+str(i)
    print("Executing "+cmd)
    runcmd(cmd)

def run_worker(task=-1):
  print("Worker %d entering server loop" %(task))
  server = tf.train.Server(clusterspec, config=default_config(),
                           job_name="worker",
                           task_index=FLAGS.task)
  server.join()

def run_client():
  tasks = ["/job:worker/task:%d"%(i) for i in range(FLAGS.num_workers)]

  (init_op, add_ops) = create_graph(tasks)
  
  # launch distributed service
  print("launching workers")
  launch_workers()

  # reset containers of first worker (it stores shared state)
  worker_ip = host+str(FLAGS.starting_port)

  # need tf.Session.reset if there are worker servers launched from before
  # However, tf.Session.reset can hang if workers are in process of being
  # brought up, hence more robust to do killall python
  #  tf.Session.reset("grpc://" + worker_ip)
  print("Creating session")
  sess = tf.Session("grpc://"+ worker_ip,
                    config=default_config())
  sess.run(init_op)
  
  worker_threads = create_worker_threads(sess)
  [t.start() for t in worker_threads]
  wait_for_threads_to_finish(worker_threads)

if __name__=='__main__':
  if FLAGS.task == -1:
    # client launches worker processes and issues .run calls
    run_client()
  else:
    run_worker(FLAGS.task)
