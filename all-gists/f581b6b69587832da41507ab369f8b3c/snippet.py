"""
Behave runner for running features asynchronously.
"""
from multiprocessing import Pool
from subprocess import call, Popen, PIPE
from glob import glob
import logging
import argparse
import json
from functools import partial

logging.basicConfig(level=logging.INFO,
                    format="[%(levelname)-8s %(asctime)s] %(message)s")
logger = logging.getLogger(__name__)


def parse_arguments():
    """
    Parses commandline arguments
    :return: Parsed arguments
    """
    parser = argparse.ArgumentParser('Run Ikarus in parallel mode')
    parser.add_argument('--processes', '-p', type=int, help='Maximum number of processes. Default = 5', default=5)
    parser.add_argument('--verbose', '-v', action='store_true', help='verbose output')
    parser.add_argument('--tags', '-t', help='specify behave tags to run')
    parser.add_argument('--define', '-D', action='append', help='Define user-specific data for the config.userdata '
                                                                'dictionary. Example: -D foo=bar to store it in '
                                                                'config.userdata["foo"].')
    args = parser.parse_args()
    return args


def _run_feature(feature, tags=None, userdata=None):
    """
    Runs features matching given tags and userdata
    :param feature: Feature that should be run
    :type feature: str
    :param tags: Tags features should contain
    :type tags: str
    :param userdata: Userdata for behave
    :type userdata: list
    :return: Feature and status
    """
    logger.debug("Processing feature: {}".format(feature))
    if not userdata:
        params = "--tags={0} --no-capture".format(tags)
    else:
        params = "--tags={0} -D {1} --no-capture".format(tags, ' -D '.join(userdata))
    cmd = "behave -f plain {0} -i {1}".format(params, feature)
    r = call(cmd, shell=True)
    status = 'ok' if r == 0 else 'failed'
    return feature, status


def main():
    """
    Runner
    """
    args = parse_arguments()
    pool = Pool(args.processes)
    if args.tags:
        p = Popen('behave -d -f json --no-summary -t {}'.format(args.tags),
                  stdout=PIPE, shell=True)
        out, err = p.communicate()
        j = json.loads(out.decode())
        features = [e['location'].replace(r'features/', '')[:-2] for e in j]
    else:
        feature_files = glob('features/*.feature') + glob('features/**/*.feature')
        features = [x.replace('features/', '') for x in feature_files]
    run_feature = partial(_run_feature, tags=args.tags, userdata=args.define)
    logger.info("Found {} features".format(len(features)))
    logger.debug(features)
    # features = [f for f in features if 'aft' not in f]
    for feature, status in pool.map(run_feature, features):
        print("{0:50}: {1}".format(feature, status))


if __name__ == '__main__':
    main()
