#!/usr/bin/env python

import roslib
roslib.load_manifest("sensor_msgs")
roslib.load_manifest("message_filters")
roslib.load_manifest("rxtools")
import rospy
import rxtools
import rxtools.rosplot
import sys
import message_filters
from optparse import OptionParser, OptionValueError

topic_desc = []
fd = False
class Error(Exception):
    pass
class InvalidTopic(Error):
    pass
class NoFieldName(Error):
    pass
class NotSupportedFeature(Error):
    pass

def usage():
    print """usage:
bag_to_ssv OUTPUT_FILE TOPIC1 [TOPIC2 TOPIC3 ...]"""
    return 1

def time_axeq(self, other):
    if not isinstance(other, roslib.rostime.Time):
        return False
    secs = abs(self.to_sec() - other.to_sec())
    # within 10msec
    if secs < tolerance:
        return True
    else:
        return False
    #return self.secs == other.secs and self.nsecs == other.nsecs

def time_cmp(self, other):
    if not isinstance(other, roslib.rostime.Time):
        raise TypeError("cannot compare to non-Time")
    secs = self.to_sec() - other.to_sec()
    if abs(secs) < tolerance:
        return 0
    if secs > 0:
        return 1
    return -1

def time_hash(self):
    return ("%s.%s"%(self.secs, self.nsecs / int(tolerance * 1e9))) .__hash__()


def callback(*values):
    for (v, evals) in zip(values, topic_desc):
        for f in evals[1]:
            v = f(v)            # update v recursively...
        fd.write(str(v) + deliminator)
    fd.write("\n")
    fd.flush()

def main(args):
    global fd
    output_file = args[1]
    fd = open(output_file, "w")
    topics = args[2:]
    subscribers = []
    # setup subscribers and topic_desc and print the first line
    for topic in topics:
        (topic_type, real_topic, rest) = rxtools.rosplot.get_topic_type(topic)
        if rest == '':
            raise NoFieldName("you need to specify filed")
        e = rxtools.rosplot.generate_field_evals(rest)
        #if len(e) > 1:
        #    raise NotSupportedFeature("sorry, currently we does not support : separate representation")
        topic_desc.append([real_topic, e])
        data_class = roslib.message.get_message_class(topic_type)
        subscribers.append(message_filters.Subscriber(real_topic, data_class))
        print "subscribing to %s" % (real_topic)
        # print line
        fd.write(topic + deliminator)
    fd.write("\n")
    ts = message_filters.TimeSynchronizer(subscribers, 100)
    
    ts.registerCallback(callback)
    try:
        rospy.spin()
    finally:
        fd.close()

def parse_options(args):
    parser = OptionParser(usage="topics_to_ssv [options] OUTPUT_FILE_NAME TOPICNAME1 TOPICNAME2 ...")
    parser.add_option("-d", "--deliminator", dest = "deliminator",
                      default = ";",
                      help = "specify deliminator character (or string). the default value is ;",
                      action = "store")
    parser.add_option("-t", "--tolerance", dest = "tolerance",
                      default = "0.04",
                      help = """specify timestamp tolerance in sec. the default value is 0.04""",
                      action = "store")
    (options, args) = parser.parse_args(args)
    # setup global variables
    global tolerance
    global deliminator
    deliminator = options.deliminator
    tolerance = float(options.tolerance)
    return args

if __name__ == "__main__":
    rospy.init_node("bag_to_ssv")
    args = parse_options(sys.argv)
    setattr(roslib.rostime.Time, "__eq__", time_axeq)
    setattr(roslib.rostime.Time, "__cmp__", time_cmp)
    setattr(roslib.rostime.Time, "__hash__", time_hash)
    main(args)
