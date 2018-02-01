#!/usr/bin/python
#
# Convert a Row-Based-Replication binary log to Statement-Based-Replication format, cheating a little.
# This script exists since Percona Toolkit's pt-query-digest cannot digest RBR format. The script
# generates enough for it to work with.
# Expecting standard input
# Expected input is the output of "mysqlbinlog --verbose --base64-output=DECODE-ROWS <binlog_file_name>"
# For example:
# $ mysqlbinlog --verbose --base64-output=DECODE-ROWS mysql-bin.000006 | python binlog-rbr-to-sbr.py | pt-query-digest --type=binlog --order-by Query_time:cnt --group-by fingerprint
#

import fileinput

def convert_rbr_to_pseudo_sbr(): 
    inside_rbr_statement = False
    for line in fileinput.input():
        line = line.strip()
        if line.startswith("#") and "end_log_pos" in line:
            for rbr_token in ["Update_rows:", "Write_rows:", "Delete_rows:", "Rows_query:", "Table_map:",]:
                if rbr_token in line:
                    line = "%s%s" % (line.split(rbr_token)[0], "Query\tthread_id=1\texec_time=0\terror_code=0")
        if line.startswith("### "):
            inside_rbr_statement = True
            # The "### " commented rows are the pseudo-statement interpreted by mysqlbinlog's "--verbose",
            # and which we will feed into pt-query-digest
            line = line.split(" ", 1)[1].strip()
        else:
            if inside_rbr_statement:
                print("/*!*/;")
            inside_rbr_statement = False
        print(line) 
        
convert_rbr_to_pseudo_sbr()
