import sys

import boto


# based on http://www.quora.com/Amazon-S3/What-is-the-fastest-way-to-measure-the-total-size-of-an-S3-bucket

# assumes you've already configured your access id & secret key
s3 = boto.connect_s3()


def get_bucket_size(bucket_name):
    '''Given a bucket name, retrieve the size of each key in the bucket
    and sum them together. Returns the size in gigabytes and
    the number of objects.'''

    bucket = s3.lookup(bucket_name)

    total_bytes = 0
    n = 0
    for key in bucket:
        total_bytes += key.size
        n += 1
        if n % 2000 == 0:
            print n
    total_gigs = total_bytes/1024/1024/1024

    print "%s: %i GB, %i objects" % (bucket_name, total_gigs, n)

    return total_gigs, n


if __name__ == '__main__':
    if len(sys.argv) > 1:
        bucket_list = sys.argv[1:]
    else:
        bucket_list = [i.name for i in s3.get_all_buckets()]

    bucket_sizes = []

    for bucket_name in bucket_list:
        size, object_count = get_bucket_size(bucket_name)
        bucket_sizes.append(dict(name=bucket_name, size=size, count=object_count))

    print "\nTotals:"
    for bucket_size in bucket_sizes:
        print "%s: %iGB, %i objects" % (bucket_size["name"], bucket_size["size"], bucket_size["count"])