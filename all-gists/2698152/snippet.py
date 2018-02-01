import os
import sys
import subprocess
import re
import optparse
import boto

dynamodb_conn = boto.connect_dynamodb(aws_access_key_id='MY_ACCESS_KEY_ID', aws_secret_access_key='MY_SECRET_ACCESS_KEY')
table_name = 'mytable'
dynamodb_table = dynamodb_conn.get_table(table_name)

BATCH_COUNT = 25

def do_batch_write(items):
    batch_list = dynamodb_conn.new_batch_write_list()
    batch_list.add_batch(dynamodb_table, puts=items)
    while True:
        response = dynamodb_conn.batch_write_item(batch_list)
        unprocessed = response.get('UnprocessedItems', None)
        if not unprocessed:
            break
        batch_list = dynamodb_conn.new_batch_write_list()
        unprocessed_list = unprocessed[table_name]
        items = []
        for u in unprocessed_list:
            item_attr = u['PutRequest']['Item']
            item = dynamodb_table.new_item(
                    attrs=item_attr
            )
            items.append(item)
        batch_list.add_batch(dynamodb_table, puts=items)

def process_log(logfile):
    item_attr = {}
    cmd = "lzop -dc %s | cat -" % logfile
    p = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE)
    cnt = 0
    items = []
    for line in iter(p.stdout.readline,''):
        line = line.rstrip('\n')
        s = re.search("(\S+)\s+(\S+)", line)
        if not s:
            continue
        (key, value) = s.groups()

        item_attr = {
            'mykey': key,
            'myvalue': value,
        }
            
        item = dynamodb_table.new_item(
                attrs=item_attr
        )
        items.append(item)
        cnt += 1
        if cnt == BATCH_COUNT:
            do_batch_write(items)
            cnt = 0
            items = []

    if cnt:
        do_batch_write(items)

def main(prog_args):
    parser = optparse.OptionParser()
    opt, args = parser.parse_args(prog_args)

    if len(args) != 2:
        print "usage: %s <logfile>" % (args[0])
        sys.exit(1)

    logfile = args[1]
    process_log(logfile)

if __name__ == '__main__':
	sys.exit(main(sys.argv))
