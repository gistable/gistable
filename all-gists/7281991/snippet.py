#!/usr/bin/env python
doc = """
Quickly estimates insert sizes of read datasets, given some sequence(s) they can be mapped to.
Author: Rayan Chikhi         

short usage: <reference> <*.fastq> 

example: 
         estimate-insert-sizes contigs.fa readsA_1.fq readsA_2.fq readsB_1.fq readsB_2.fq

or, with shell globbing:
         
         estimate-insert-sizes contigs.fa *.fq

special case, a single argument is interpreted as interleaved pairs:
         
         estimate-insert-sizes contigs.fa interleaved.fq
"""

""" technical note:
 by default, bwa will be executed with "-t X" to read X*100kbp sequences, instead of just 100kbp.
 100kbp is not enough in my experience to detect insert sizes.
 incidentally, bwa will use X threads, even if the cpu has less cores than that.
 X can be changed by modifying this variable:
"""

nb_threads = 5

# --------

from glob import glob
import subprocess
import sys, os

if len(sys.argv) < 3:
    exit(doc)

reference = sys.argv[1]
reads = sorted(sys.argv[2:])

try:
    subprocess.call(["bwa"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
except:
    exit("Please make sure that the `bwa` binary is in your $PATH")

for read in reads:
    if not os.path.isfile(read):
        exit("Error: %s does not exist" % read)

if len(reads) == 1:
    print "Assuming that %s is interleaved" % reads[0]
    reads += [""]

if not os.path.isfile(reference+".sa"):
    print "Creating index file.."
    subprocess.call(["bwa", "index", reference], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def parse_list(line, nb_elts):
    # specific to BWA-MEM stderr format
    return map(lambda x: int(float(x)), ' '.join(line.strip().replace(',','').split()[-nb_elts:])[1:-1].split())

stats = dict()
for read1, read2 in zip(reads[::2],reads[1::2]):
    print( "Processing: \n %s \n %s " % (read1,read2) )
    cmd = ["bwa", "mem"] + (["-p"] if read2 == "" else []) +  ["-t %d" % nb_threads, reference, read1, read2]
    DEVNULL = open(os.devnull, 'wb')
    process = subprocess.Popen(cmd, stdout=DEVNULL, stderr=subprocess.PIPE)
    seen_candidate_line = False
    while True:
        line = process.stderr.readline()
        if line == '' and process.poll() != None:
            break
        if "worker" in line:
            break
        if "pestat" not in line:
            continue
        if "candidate unique pairs for" in line:
            if seen_candidate_line:
                break
            seen_candidate_line = True
            nb_pairs = parse_list(line,4)
            for i in xrange(4):
                stats[['FF', 'FR', 'RF', 'RR'][i]] = { 'nb_pairs' : nb_pairs[i] }
        if "orientation" in line:
            orientation = line.strip().split()[-1].replace('.','')
        if "mem_pestat] mean and std.dev:" in line:
            mean, stdev = parse_list(line,2)
            stats[orientation]['mean'] = mean
            stats[orientation]['stdev'] = stdev
            if orientation == 'RR':
                # stats are complete
                break
        sys.stdout.write(line)
        sys.stdout.flush()
    if process.poll() is None:
        process.terminate()
   
    results = sorted(stats.items(), key = lambda x: x[1]['nb_pairs'], reverse=True)
    most_likely = results[0]
    mean = most_likely[1]['mean']
    stdev = most_likely[1]['stdev']
    print "Orientation", most_likely[0], "mean", mean, "stdev", stdev
