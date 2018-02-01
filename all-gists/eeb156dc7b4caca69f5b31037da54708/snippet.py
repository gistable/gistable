## https://gist.github.com/pierriko/fd49abfa2fb3561f9c89
## https://github.com/omgteam/Didi-competition-solution
## https://discussions.udacity.com/t/processing-velodyne-data-for-dataset-2/237084/7

#  attach process: https://www.jetbrains.com/help/pycharm/2016.3/attaching-to-local-process.html

import sys
##sys.path.insert(0,'/opt/ros/kinetic/lib/python2.7/dist-packages')
##sys.path.insert(0,'/usr/lib/python2.7/dist-packages')  ## rospkg

import os
#os.system('source /opt/ros/kinetic/setup.bash')

import numpy as np
import rospy
from sensor_msgs.msg import PointCloud2, PointField

#---------------------------------------------------------------------------------------------------------

# PointCloud2 to array
# 		https://gist.github.com/dlaz/11435820
#       https://github.com/pirobot/ros-by-example/blob/master/rbx_vol_1/rbx1_apps/src/point_cloud2.py
#       http://answers.ros.org/question/202787/using-pointcloud2-data-getting-xy-points-in-python/
#       https://github.com/eric-wieser/ros_numpy/blob/master/src/ros_numpy/point_cloud2.py



# https://github.com/eric-wieser/ros_numpy #############################################################################################

DUMMY_FIELD_PREFIX = '__'

# mappings between PointField types and numpy types
type_mappings = [(PointField.INT8, np.dtype('int8')), (PointField.UINT8, np.dtype('uint8')), (PointField.INT16, np.dtype('int16')),
                 (PointField.UINT16, np.dtype('uint16')), (PointField.INT32, np.dtype('int32')), (PointField.UINT32, np.dtype('uint32')),
                 (PointField.FLOAT32, np.dtype('float32')), (PointField.FLOAT64, np.dtype('float64'))]

pftype_to_nptype = dict(type_mappings)
nptype_to_pftype = dict((nptype, pftype) for pftype, nptype in type_mappings)

# sizes (in bytes) of PointField types
pftype_sizes = {PointField.INT8: 1, PointField.UINT8: 1, PointField.INT16: 2, PointField.UINT16: 2,
                PointField.INT32: 4, PointField.UINT32: 4, PointField.FLOAT32: 4, PointField.FLOAT64: 8}



def fields_to_dtype(fields, point_step):
    '''
    Convert a list of PointFields to a numpy record datatype.
    '''
    offset = 0
    np_dtype_list = []
    for f in fields:
        while offset < f.offset:
            # might be extra padding between fields
            np_dtype_list.append(('%s%d' % (DUMMY_FIELD_PREFIX, offset), np.uint8))
            offset += 1

        dtype = pftype_to_nptype[f.datatype]
        if f.count != 1:
            dtype = np.dtype((dtype, f.count))

        np_dtype_list.append((f.name, dtype))
        offset += pftype_sizes[f.datatype] * f.count

    # might be extra padding between points
    while offset < point_step:
        np_dtype_list.append(('%s%d' % (DUMMY_FIELD_PREFIX, offset), np.uint8))
        offset += 1

    return np_dtype_list




def msg_to_arr(msg):

    dtype_list = fields_to_dtype(msg.fields, msg.point_step)
    arr = np.fromstring(msg.data, dtype_list)

    # remove the dummy fields that were added
    arr = arr[[fname for fname, _type in dtype_list if not (fname[:len(DUMMY_FIELD_PREFIX)] == DUMMY_FIELD_PREFIX)]]

    if msg.height == 1:
        return np.reshape(arr, (msg.width,))
    else:
        return np.reshape(arr, (msg.height, msg.width))

##################################################################################################################################

lidar_dir = '/root/share/project/didi/data/didi/didi-2/Data/1/15/lidar'
##lidar_dir = '/root/share/project/didi/data/didi/didi-2/Out/Round_1_Test/19_f2/lidar'

def callback(msg):

    timestamp = msg.header.stamp.to_nsec()


    print('callback: msg : seq=%d, timestamp=%19d'%(
        msg.header.seq, timestamp
    ))
    arr= msg_to_arr(msg)
    file=lidar_dir+'/%19d.npy'%(
        timestamp
    )
    np.save(file,arr)

    #dd=0
    pass



if __name__=='__main__':
    print( '%s: calling main function ... ' % os.path.basename(__file__))

    if not os.path.exists(lidar_dir):
        os.makedirs(lidar_dir)

    rospy.init_node('velodyne_subscriber')
    velodyne_subscriber = rospy.Subscriber('/velodyne_points', PointCloud2, callback)
    rospy.spin()

    print( 'success' )