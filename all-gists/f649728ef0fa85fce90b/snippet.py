#!/usr/bin/env python
# coding=utf-8
"""
Runs bcl2fastq creating fastqs and concatenates fastqs across lanes. Intended
to be used with NextSeq data and it does not do any cleanup! Original dumped
fastqs will remain along with all of the bcl files.
"""

from __future__ import print_function

import fileinput
import os
import string
import subprocess as sp
import sys
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, REMAINDER
from itertools import izip_longest


_complement = string.maketrans("ATCG", "TAGC")
complement = lambda seq: seq.translate(_complement)


def process_samplesheet(samplesheet, reverse_complement):
    samples = []
    experiment = ""

    try:
        start = False
        experiment_idx = 0
        index2_idx = None
        # strip whitespace and rewrite file in place
        for toks in fileinput.input(samplesheet, mode='rU', backup='.bak', inplace=True):
            toks = toks.rstrip("\r\n").split(',')

            if not start:
                if toks[0] == "Sample_ID":
                    start = True
                    experiment_idx = toks.index("Sample_Project")
                    if reverse_complement:
                        if "index2" in toks:
                            index2_idx = toks.index("index2")
                        elif "Index2" in toks:
                            index2_idx = toks.index("Index2")

                print(",".join([t.strip() for t in toks]))

            # remove blank lines at end of table
            elif toks[0]:
                # bcl2fastq converts underscores to dashes
                samples.append(toks[0].replace("_", "-").replace(".", "-"))
                # location of fastq output
                if not experiment:
                    experiment = toks[experiment_idx]
                # only adjust on known index
                if reverse_complement and index2_idx:
                    toks[index2_idx] = complement(toks[index2_idx])[::-1]
                print(",".join([t.strip() for t in toks]))

    finally:
        fileinput.close()

    if reverse_complement and not index2_idx:
        sys.exit("Unable to reverse complement index2 of the SampleSheet. " +
            "Avoid using 'reverse-complement' or check your SampleSheet.csv " +
            "for 'index2' header.")

    return samples, experiment


def wait_for_completion(runfolder_dir):
    import time
    from xml.etree import ElementTree

    run_document = os.path.join(runfolder_dir, "RunCompletionStatus.xml")
    sleep_time = 1
    notify = True
    while not os.path.exists(run_document):
        if notify:
            print("Waiting on run completion.")
            notify = False
        time.sleep(sleep_time)
        if sleep_time < 60:
            sleep_time += 1
    print("Run complete.")

    try:
        doc = ElementTree.parse(run_document)
        run_status = doc.find("CompletionStatus").text
    except IOError:
        sys.exit("Could not find %s. Exiting." % run_document)
    except AttributeError:
        sys.exit("Error parsing %s. Exiting." % run_document)

    return True if run_status == "CompletedAsPlanned" else False


def main(runfolder_dir, loading_threads, demultiplexing_threads,
    processing_threads, barcode_mismatches, wait, reverse_complement, args):

    # verify working directory
    samplesheet = os.path.join(runfolder_dir, "SampleSheet.csv")
    if not os.path.exists(samplesheet):
        sys.exit("%s was not found. Exiting." % samplesheet)

    # get sample names and experiment name from SampleSheet
    samples, experiment = process_samplesheet(samplesheet, reverse_complement)
    if len(samples) == 0:
        sys.exit("No samples were found in the SampleSheet. Check formatting.")

    # execute and wait on run completion
    if wait:
        completion_success = wait_for_completion(runfolder_dir)
        if not completion_success:
            sys.exit("Run did not complete as planned. Exiting.")

    # set args for call to bcl2fastq
    if not '-w' in args or '--writing-threads' in args:
        args.append('--writing-threads')
        args.append(len(samples))
    args.extend(['-R', runfolder_dir, '-r', loading_threads, '-d',
        demultiplexing_threads, '-p', processing_threads,
        '--barcode-mismatches', barcode_mismatches])
    args.insert(0, 'bcl2fastq')

    # run bcl2fastq
    bcl2fastq_log = os.path.join(runfolder_dir, "bcl2fastq.log")
    cmd = " ".join(map(str, args))
    print("Converting .bcl to .fastq using:")
    print("$>", cmd)
    with open(bcl2fastq_log, 'w') as fh:
        # bcl2fastq version info...
        sp.check_call("bcl2fastq --version 2>&1 | tail -2 | head -1",
            stdout=fh, stderr=fh, shell=True)
        # the actual call
        sp.check_call(cmd, stdout=fh, stderr=fh, shell=True)
    print(".bcl conversion was successful")

    # location of fastqs from bcl2fastq
    if '-o' in args:
        output_dir = args[args.index('-o') + 1]
    elif '--output-dir' in args:
        output_dir = args[args.index('--output-dir') + 1]
    else:
        output_dir = os.path.join(runfolder_dir, "Data", "Intensities", "BaseCalls")
    output_dir = os.path.join(output_dir, experiment)

    # build `cat` commands to join files across lanes
    commands = []
    for i, sample in enumerate(samples, start=1):
        for read in ['R1', 'R2']:
            cmd = ['cat']
            result_file = "%s/%s_%s.fastq.gz" % (output_dir, sample, read)
            for lane in [1, 2, 3, 4]:
                # build the files paths
                path = "%s/%s_S%d_L00%d_%s_001.fastq.gz" % \
                    (output_dir, sample, i, lane, read)
                if not os.path.exists(path):
                    sys.exit("Can't find %s. Concatenation failed." % path)
                cmd.append(path)

            # using shell to ease redirection
            commands.append(" ".join(cmd) + " > " + result_file)

    # execute concatenation 4 samples at a time
    print("Joining reads across lanes")
    groups = [(sp.Popen(cmd, shell=True) for cmd in commands)] * 4
    for processes in izip_longest(*groups):
        for p in filter(None, processes):
            p.wait()


if __name__ == '__main__':
    p = ArgumentParser(description=__doc__, formatter_class=ArgumentDefaultsHelpFormatter)
    p.add_argument('-R', '--runfolder-dir', default=".", help="path to run folder")
    p.add_argument('-r', '--loading-threads', default=12, type=int,
        help="threads used for loading BCL data")
    p.add_argument('-d', '--demultiplexing-threads', default=12, type=int,
        help="threads used for demultiplexing")
    p.add_argument('-p', '--processing-threads', default=12, type=int,
        help="threads used for processing demultiplexed data")
    p.add_argument('--barcode-mismatches', default=0, type=int,
        help="number of allowed mismatches per index")
    p.add_argument('--reverse-complement', action='store_true',
        help="reverse complement Index 2 of the Sample Sheet")
    p.add_argument('--wait', action='store_true',
        help="wait for run to complete; checks completion status in RunCompletionStatus.xml")
    # p.add_argument('args', nargs=REMAINDER,
        # help="any additional bcl2fastq args and their values")
    # args = vars(p.parse_args())

    # need to let user know they can pass additional args...
    args, leftovers = p.parse_known_args()
    args = vars(args)
    args['args'] = leftovers
    main(**args)
