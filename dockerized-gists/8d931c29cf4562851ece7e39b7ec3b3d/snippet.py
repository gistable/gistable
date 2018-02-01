# Script to migrate jenkins job from one server to another via cli
# Make sure python-jenkins is installed in order to use script

import argparse
import jenkins

def get_parser():
  parser = argparse.ArgumentParser()
  parser.add_argument('-j', '--job_name', type=str, required=True, help='Name of job that is to be migrated')
  parser.add_argument('-o', '--original_server', type=str, required=True, help='Server to migrate from')
  parser.add_argument('--o_uname', type=str, required=True, help='Valid username on original server')
  parser.add_argument('--o_passwd', type=str, required=True, help='Password for valid username on original server')
  parser.add_argument('-t', '--target_server', type=str, required=True, help='Target server to move job too')
  parser.add_argument('--t_uname', type=str, required=True, help='Valid username on target server')
  parser.add_argument('--t_passwd', type=str, required=True, help='Password for valid username on target server')
  
  return parser

def main(job_name, orig_server, orig_uname, orig_passwd, target_server, target_uname, target_passwd):
  
  # Create instances of both servers
  orig_jenkins = jenkins.Jenkins(orig_server, orig_uname, orig_passwd)
  target_jenkins = jenkins.Jenkins(target_server, target_uname, target_passwd)
  
  # Get config.xml from original jenkins server
  config_xml = orig_jenkins.get_job_config(job_name)
  
  # Create new job on target server using job name and retrieved config.xml
  target_jenkins.create_job(job_name, config_xml)
  
if __name__ == '__main__':
  parser = get_parser()
  args = parser.parse_args()
  main(args.job_name, args.original_server, args.o_uname, args.o_passwd, args.target_server, args.t_uname, args.t_passwd)
