import re
from boto.ec2.cloudwatch import CloudWatchConnection
from boto.utils import get_instance_metadata

def collect_memory_usage_for_instance():
    """
    Function to collect EC2 Memory Metrics
    :return:
    """
    meminfo = {}
    pattern = re.compile('([\w\(\)]+):\s*(\d+)(:?\s*(\w+))?')
    with open('/proc/meminfo') as f:
        for line in f:
            match = pattern.match(line)
            if match:
                meminfo[match.group(1)] = float(match.group(2))
    return meminfo


def send_multi_metrics(instance_id, metrics, namespace='EC2/Memory', unit='Percent'):
    """
    Function to send metrics to AWS CloudWatch
    :param instance_id:
    :param metrics:
    :param namespace:
    :param unit:
    :return:
    """
    cloud_watch_connection = CloudWatchConnection(aws_access_key_id='',
                                                  aws_secret_access_key="")
    try:
        print cloud_watch_connection.put_metric_data(namespace, metrics.keys(), metrics.values(),
                                                     unit=unit,
                                                     dimensions={"InstanceId": instance_id})
    except Exception as e:
        print(e)


if __name__ == '__main__':
    # Main function to be executed first
    metadata = get_instance_metadata()
    instance_id = metadata['instance-id']
    region = metadata['placement']['availability-zone'][0:-1]
    # Collecting memory metrics of the instance to mem_usage_metrics: a Python Dict
    mem_usage_metrics = collect_memory_usage_for_instance()
    mem_total = mem_usage_metrics['MemTotal']
    # Free memory is total of free memory, cached memory and buffer memory
    mem_free = mem_usage_metrics['MemFree'] + mem_usage_metrics['Buffers'] + mem_usage_metrics['Cached']
    mem_used = mem_usage_metrics['MemTotal'] - mem_free
    if mem_usage_metrics['SwapTotal'] != 0:
        swap_used = mem_usage_metrics['SwapTotal'] - mem_usage_metrics['SwapFree'] - mem_usage_metrics['SwapCached']
        swap_percent = swap_used / mem_usage_metrics['SwapTotal'] * 100
    else:
        swap_percent = 0

    # Metrics to be stored in AWS Cloudwatch
    metrics = {'MemoryUtilization': mem_used / mem_usage_metrics['MemTotal'] * 100,
               'SwapUsage': swap_percent,
               'MemoryUsed': mem_used,
               'MemoryAvailable': mem_usage_metrics['MemAvailable'],
               'SwapTotal': mem_usage_metrics['SwapTotal'],
               'SwapFree': mem_usage_metrics['SwapFree']}

    # Calling Function to send metrics to Cloudwatch
    send_multi_metrics(instance_id, metrics)
