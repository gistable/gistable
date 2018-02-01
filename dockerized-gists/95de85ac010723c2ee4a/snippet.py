#!/usr/bin/env python

"""Extend HITs as assignments are completed.

If a HIT takes up a lot of bandwidth, then you may only want to have a
few workers doing it at a time. This script monitors how many
assignments are currently being worked on, and as they are completed,
extends the HIT with new assignments until a specified upper limit is
reached.


The MIT License (MIT)

Copyright (c) 2014 Jessica B. Hamrick <jhamrick@berkeley.edu>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""

import time
import datetime
import logging
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from boto.mturk.connection import MTurkConnection

logging.basicConfig(level="INFO", format="%(asctime)s -- %(message)s")


if __name__ == "__main__":
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        "hit",
        metavar="HIT",
        help="HIT id.")
    parser.add_argument(
        "concurrent",
        metavar="NUM_CONCURRENT",
        type=int,
        help="Number of concurrent assignments.")
    parser.add_argument(
        "total",
        metavar="NUM_TOTAL",
        type=int,
        help="Number of total assignments.")
    parser.add_argument(
        "-i", "--interval",
        type=int,
        default=60,
        help="Number of seconds to wait before checking HIT again.")
    parser.add_argument(
        "-a", "--approve",
        default=False,
        action="store_true",
        help="Whether to automatically approve submitted assignments.")

    args = parser.parse_args()

    # connect to turk
    conn = MTurkConnection("aws_access_key_id", "aws_secret_access_key")

    while True:
        # get information about the HIT
        hit, = conn.get_hit(args.hit, ['HITDetail', 'HITAssignmentSummary'])
        total = int(hit.MaxAssignments)
        pending = int(hit.NumberOfAssignmentsPending)
        complete = int(hit.NumberOfAssignmentsCompleted)
        available = int(hit.NumberOfAssignmentsAvailable)
        logging.info(
            "max:%s/pending:%s/complete:%s/remain:%s",
            total, pending, complete, available)

        # check if we have reached the total
        if total >= args.total:
            logging.info("MaxAssignments = %s, exiting", total)
            break
            
        # compute how many assignments are currently outstanding
        current = available + pending
        if current < args.concurrent:
            diff = min(args.total - total, args.concurrent - current)
            logging.info("Extending HIT with %s more assignments", diff)
            conn.extend_hit(args.hit, assignments_increment=diff)

        # get submitted assignments and approve them
        if args.approve:
            assignments = conn.get_assignments(args.hit, status="Submitted", page_size=100)
            for assignment in assignments:
                logging.info("Approving assignment %s", assignment.AssignmentId)
                conn.approve_assignment(assignment.AssignmentId, feedback=None)

        time.sleep(args.interval)