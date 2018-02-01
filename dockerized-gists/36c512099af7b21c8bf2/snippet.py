#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
 AUTHOR: Gabriel Bassett
 DATE: 11-19-2014
 DEPENDENCIES: py2neo
 Copyright 2014 Gabriel Bassett


 LICENSE:
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at
  http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.

 DESCRIPTION:
  A tool for importing a netflow CSV 

"""
# PRE-USER SETUP
from __future__ import print_function

########### NOT USER EDITABLE ABOVE THIS POINT #################


# USER VARIABLES
FILE = "~/Documents/flows.csv"
SHIFT=0 # 0 for raw netflow output, 1 for pandas as it adds a column
BATCH_SIZE = 500  # The number of records to process per batch
COMMIT_SIZE = BATCH_SIZE * 10  # multiplied by the batch size to get the number of records to wait for to commit
NEODB = "http://localhost:7474/db/data"


########### NOT USER EDITABLE BELOW THIS POINT #################

## IMPORTS

from time import time
import csv
import argparse
from py2neo import Graph, Node, GraphError
 
## SETUP
__author__ = "Gabriel Bassett"
# Parse Arguments (should correspond to user variables)
parser = argparse.ArgumentParser(description='This imports netflow into a neo4j database.')
# <add arguments here>
parser.add_argument('file', help='Input file.', default=FILE)
parser.add_argument('--db', help='URL of the neo4j graph database', default=NEODB)
parser.add_argument('-i', '--index', help='Indicates the first row is an index.', action='store_const', dest='shift', const=1, default=SHIFT)
parser.add_argument('-b', '--batch', help='How many cyphers to parse per batch.  Default is 500.  Should be in hundreds.', dest='batch', default=COMMIT_SIZE)
parser.add_argument('-c', '--commit', help='How many cyphers to commit at a time.  Default is 10x batch.  Should be in thousands.', dest='commit', default=COMMIT_SIZE)
args = parser.parse_args()
NEODB = args.db
FILE = args.file
SHIFT = args.shift
 
## EXECUTION
def main():
    graph = Graph(NEODB)
    create_node_statement = (
        "MERGE(a: attribute {ip:{IP}})"
        "ON CREATE SET a = {ip:{IP}, asn:{ASN}, country:{COUNTRY}}"
    )
    create_relationship_statement = (
        "MATCH (a: attribute), (b: attribute) "
        "WHERE a.ip = {SRC_IP} AND b.ip = {DST_IP} "
        "MERGE (a)-[rel: flow {start_time:{START_TIME}, "
        "                              end_time:{END_TIME}"
        "}]->(b)"
        "ON CREATE SET rel = {duration:{DURATION}, "
        "                     proto:{PROTO}, "
        "                     src_port:{SRC_PORT}, "
        "                     dst_port:{DST_PORT}, "
        "                     flags:{FLAGS}, "
        "                     packets:{PACKETS}, "
        "                     bytes:{BYTES}, "
        "                     log_time:{LOG_TIME}}"
        "RETURN rel"
    )
    # Ensure uniqueness for nodes
    try:
        graph.schema.create_uniqueness_constraint("attribute", "ip")
    except:
        pass
    # Below for transactional creation of nodes to allow bulk merge.
    print("Starting node processing")
    l = 1
    k = 1
    t0 = time()
    ips = set()
    last_ips_len = 0
    tx = graph.cypher.begin()
    with open(FILE, "r") as f:
        linereader=csv.reader(f)
        _ = linereader.next()
        for line in linereader:
            try:
                if line[3+SHIFT] not in ips:
                    src_attr = {
                        "IP": line[3+SHIFT],
                        "ASN": int(line[15+SHIFT]),
                        "COUNTRY": line[17+SHIFT]
                    }
                    tx.append(create_node_statement, src_attr)
                    ips.add(line[3+SHIFT])
                if line[4+SHIFT] not in ips:
                    dst_attr = {
                        "IP": line[4+SHIFT],
                        "ASN": int(line[16+SHIFT]),
                        "COUNTRY": line[18+SHIFT]
                    }
                    tx.append(create_node_statement, dst_attr)
                    ips.add(line[4+SHIFT])
                ips_len = len(ips)
                if ips_len % COMMIT_SIZE == 0 and ips_len != last_ips_len:
                    print("Committing nodes from line {0} to {1}".format(k, ips_len))
                    k = ips_len + 1
                    tx.process()
                    tx.commit()
                    tx = graph.cypher.begin()
                elif ips_len % BATCH_SIZE == 0 and ips_len != last_ips_len:
                    print("Processing nodes from {0} to {1}".format(l, ips_len))
                    l = ips_len + 1
                    tx.process()
                last_ips_len = len(ips)
            except:
                print("Line: {0}".format(line))
                print("Line Number: {0}".format(linereader.line_num))
                print(src_attr)
                print(dst_attr)
                raise
    print("Committing nodes from {0} to {1}".format(k, ips_len))
    tx.commit()
    t1 = time()
    print("Created %d nodes in %f seconds" % (linereader.line_num, t1 - t0))

    print("Starting Edge Processing")
    t0 = time()
    tx = graph.cypher.begin()
    j = 1
    k = 1
    with open(FILE, "r") as f:
        linereader=csv.reader(f)
        _ = linereader.next()
        for line in linereader:
            try:
                attr = {
                    'START_TIME': line[0+SHIFT],
                    'END_TIME': line[1+SHIFT],
                    'DURATION': float(line[2+SHIFT]),
                    'PROTO': line[5+SHIFT],
                    'SRC_PORT': int(line[6+SHIFT]),
                    'DST_PORT': int(line[7+SHIFT]),
                    'FLAGS': line[8+SHIFT],
                    'PACKETS': int(line[9+SHIFT]),
                    'BYTES': int(line[10+SHIFT]),
                    'LOG_TIME': line[14+SHIFT],
                    'SRC_IP': line[3+SHIFT],
                    'DST_IP': line[4+SHIFT]
                }
                tx.append(create_relationship_statement, attr)
                if linereader.line_num % COMMIT_SIZE == 0:
                    print("Committing edges from {0} to {1}".format(k, linereader.line_num))
                    k = linereader.line_num + 1
                    tx.process()
                    tx.commit()
                    tx = graph.cypher.begin()
                elif linereader.line_num % BATCH_SIZE == 0:
                    print("Processing edges from {0} to {1}".format(j, linereader.line_num))
                    j = linereader.line_num + 1
                    tx.process()
            except:
                print("Line: {0}".format(line))
                print("Line Number: {0}".format(linereader.line_num))
                print(attr)
                raise
    print("Committing edges from {0} to {1}".format(j, linereader.line_num))
    tx.commit()
    t1 = time()
    print("Created %d relationships in %f seconds" % (linereader.line_num, t1 - t0))
 
 
if __name__ == "__main__":
    # Run this script against a fresh database then use the browser to explore
    # the data created with a query such as `MATCH (p:Person {user_id:1}) RETURN p`
    main()