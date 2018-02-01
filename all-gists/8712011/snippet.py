class ConnectPythonLoggingToROS(logging.Handler):

    MAP = {
        logging.DEBUG:rospy.logdebug,
        logging.INFO:rospy.loginfo,
        logging.WARNING:rospy.logwarn,
        logging.ERROR:rospy.logerr,
        logging.CRITICAL:rospy.logfatal
    }

    def emit(self, record):
        try:
            self.MAP[record.levelno]("%s: %s" % (record.name, record.msg))
        except KeyError:
            rospy.logerr("unknown log level %s LOG: %s: %s" % (record.levelno, record.name, record.msg))

#reconnect logging calls which are children of this to the ros log system
logging.getLogger('trigger').addHandler(ConnectPythonLoggingToROS())
#logs sent to children of trigger with a level >= this will be redirected to ROS
logging.getLogger('trigger').setLevel(logging.DEBUG)

rospy.init_node('triggerbox_host', log_level=rospy.DEBUG)
