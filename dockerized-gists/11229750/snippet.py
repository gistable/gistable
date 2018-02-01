#!/usr/bin/python -tt
#
import datetime
import json
import logging
import logging.handlers
import optparse
import os
import re
import shutil
import sys
import tarfile
import tempfile
import urllib2

def grafana_dashboards_backup():

  parser = optparse.OptionParser()

  parser.add_option('-D', '--debug',
        action  = 'store_true',
        default = False,
        dest    = 'debug',
        help    = 'Debug output (very noisy)')

  parser.add_option('-e', '--grafana-elasticsearch-host',
    dest    = 'elastic_host',
    help    = 'The elastic search host FQDN used by grafana',
    metavar = 'ELASTIC_SEARCH_HOST')

  parser.add_option('-p', '--grafana-elasticsearch-port',
    default = '9200',
    dest    = 'elastic_port',
    help    = 'The elastic search port used by grafana',
    metavar = 'ELASTIC_SEARCH_PORT')

  parser.add_option('-t', '--dest-dir',
    default = '/var/opt/grafana-dashboards-backups',
    dest    = 'dest_dir',
    help    = 'The destination directory where dashboards will be saved',
    metavar = 'DEST_DIR')

  (options, args) = parser.parse_args()

  if not options.elastic_host:
    parser.error('An elastic search host is required')

  elastic_host = options.elastic_host
  elastic_port = options.elastic_port
  dest_dir = options.dest_dir
  debug = options.debug

  #Set Logging to syslog
  try:
    logger = logging.getLogger(__name__)
    if debug:
      logger.setLevel(logging.DEBUG)
    else:
      logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(pathname)s: %(message)s')

    syslog_handler = logging.handlers.SysLogHandler(address = '/dev/log')
    syslog_handler.setFormatter(formatter)
    logger.addHandler(syslog_handler)
  except Exception:
    logging.info('Could not set syslog logging handler')


  def cam_case_convert(name):
    '''strips spaces and replace CamCasing.cam with cam_casing_cam'''

    s1 = re.sub('([^._])([A-Z][a-z]+)', r'\1_\2', name.replace(' ',''))
    s1 = s1.replace('.','_')
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

  # Conveniance vars
  dashboards_url = 'http://%s:%s/grafana-dash/dashboard/_search' % (elastic_host,
  elastic_port)
  work_tmp_dir = tempfile.mkdtemp()
  utc_datetime = datetime.datetime.utcnow()
  formatted_time = utc_datetime.strftime("%Y-%m-%d-%H%MZ")

  try:
    elastic_response = urllib2.urlopen(dashboards_url, timeout=5)
  except urllib2.URLError as e:
    if debug:
      logger.critical('Failed accessing: %s \n' % dashboards_url)
    logger.critical(e)
    sys.exit(1)

  if debug:
    logger.info('Grabbing grafana dashboards from: %s \n' % dashboards_url)

  try:
    data = json.load(elastic_response)
    if debug:
      print 'Elastic Search raw json:\n'
      print '-----------------------'
      print json.dumps(data, sort_keys = False, indent = 4)
  except Exception as e:
    logger.critical(e)
    sys.exit(1)

  # Create a tarball with all the dashboards and move to target dir

  tarball = os.path.join(work_tmp_dir, 'grafana_dashboards_backup_' +
      formatted_time + '.tar.gz')
  tar = tarfile.open(tarball, 'w:gz')

  try:
    for hit in data['hits']['hits']:
      dashboard_definition = json.loads(hit['_source']['dashboard'])
      dashboard_file_name = os.path.join(work_tmp_dir,
    cam_case_convert(hit['_id']) + '_' + formatted_time + '.json')
      dashboard_file = open(dashboard_file_name, 'w')
      json.dump(dashboard_definition, dashboard_file, sort_keys = True,
          indent = 2, ensure_ascii=False)
      logger.info('Added %s to the dashboards backup tarball' % hit['_id'])
      dashboard_file.close()
      tar.add(dashboard_file_name)
    tar.close()
  except Exception as e:
    logging.critical(e)
    sys.exit(1)

  try:
    tarball_file = os.path.basename(tarball)
    tarball_dest = os.path.join(dest_dir, tarball_file)
    os.rename(tarball,tarball_dest)
    logger.info('New grafana dashboards backup at %s' % tarball_dest)
  except Exception as e:
    logging.critical('Failed to move tarball to %s' % dest_dir)
    logging.critical(e)
    sys.exit(1)

  # Clean up
  try:
    shutil.rmtree(work_tmp_dir)
  except Exception as e:
    logging.critical(e)
    sys.exit(1)

def main():
  grafana_dashboards_backup

if __name__ == '__main__':
  main()