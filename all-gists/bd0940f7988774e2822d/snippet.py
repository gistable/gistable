# coding: utf-8

# command example:
#   $ spark-submit spark_log_extract.py \
#   --name test \
#   --notblankkeys dn,stm,ev_ac,pg_url \
#   --filterregex ".*(=ac_pl\`|=ac_dl\`).*" \
#   --usegzip \
#   /path/to/source \
#   /path/to/atom \
#   dn,stm,ev_ac,v_title,v_uri,pg_url

import sys
import re
from pyspark import SparkContext, SparkConf
from optparse import OptionParser


def process(line, keys=[], not_blank_keys=[]):
    fields = line.split('`')
    output_lst = [''] * len(keys)
    try:
        for field in fields:
            key, val = field.split('=', 1)
            if key in keys:
                output_lst[keys.index(key)] = val
        for not_blank_key in not_blank_keys:
            if not output_lst[keys.index(not_blank_key)]:
                return
    except:
        return
    return '\t'.join(output_lst)


def parse_args():
    usage = "usage: %prog [options] input_path output_path keys"
    parser = OptionParser(usage=usage)
    parser.add_option(
        '--name', default='SparkLogExtract', help='name of Spark job')
    parser.add_option('--notblankkeys', default=[],
                      help='field keys must be not blank with "," delimiter')
    parser.add_option(
        '--filterregex', help='line filter regex', default='.*')
    parser.add_option('--usegzip', action='store_true',
                      help='output gzip or normal file', default=False)
    (options, args) = parser.parse_args()
    if len(args) != 3:
        parser.error('incorrect number of arguments')
    return options, args


def main():
    options, args = parse_args()
    keys = [k.strip() for k in args[2].split(',')]
    not_blank_keys = [k.strip() for k in options.notblankkeys.split(',')]
    conf = SparkConf().setAppName(options.name)
    if options.usegzip:
        conf.set(
            'spark.hadoop.mapreduce.output.fileoutputformat.compress', 'true')
        conf.set('spark.hadoop.mapreduce.output.fileoutputformat.compress.codec',
                 'org.apache.hadoop.io.compress.GzipCodec')
        conf.set(
            'spark.mapreduce.output.fileoutputformat.compress.type', 'BLOCK')
    sc = SparkContext(conf=(conf))
    sc.textFile(args[0]).filter(lambda x: re.match(options.filterregex, x)).map(
        lambda x: process(x, keys, not_blank_keys)).filter(lambda x: x).saveAsTextFile(args[1])

if __name__ == '__main__':
    main()