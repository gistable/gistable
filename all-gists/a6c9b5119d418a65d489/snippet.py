#!/usr/bin/python

import requests
import os
import boto.ec2
import sys
import re

build_url = os.environ['BUILD_URL']
jenkins_base_url = os.environ['JENKINS_URL']
ami_profile_name = os.environ['AMI_PROFILE_NAME']
jenkins_auth_user = os.environ['JENKINS_AUTH_USER']
jenkins_auth_password = os.environ['JENKINS_AUTH_PASSWORD']
aws_region = os.getenv('AWS_REGION', 'us-east-1')
ec2_cloud_instance = os.getenv('EC2_CLOUD_INSTANCE', 'aws_us-east-1')
output_error_string = os.getenv('OUTPUT_ERROR_STRING', 'Error:')
build_output_text = ""

def get_jenkins_build_output():
    global build_url
    global build_output_text

    if build_output_text:
        return build_output_text

    if not build_url.endswith('/'):
        build_url = '%s/' % build_url
    jenkins_url = '%slogText/progressiveText' % build_url

    payload = {'start': '1'}
    r = requests.post(jenkins_url, verify=False, data=payload)
    if not r.status_code == 200:
        print 'HTTP POST to Jenkins URL %s resulted in %s' % (jenkins_url, r.status_code)
        print r.headers
        print r.text
        sys.exit(1)

    return r.text

def get_error_lines(build_output):
    retval = ""
    regex = re.compile(r'(.*%s.*)' % output_error_string, re.MULTILINE)
    matches = [m.groups() for m in regex.finditer(build_output)]
    if matches:
        retval = "**************************************************\n"
        retval += " Error string: '%s'\n" % output_error_string
        retval += " Found the following errors in the build output\n"
        retval += "**************************************************\n"
        for m in matches:
            retval += '%s\n' % m[0]
        retval += "**************************************************\n"
    return retval

def get_packer_ami_id(build_output):
    regex = re.compile(r'.*,amazon-ebs,artifact,.*(ami-.*)$', re.MULTILINE)
    matches = [m.groups() for m in regex.finditer(build_output)]
    for m in matches:
        return m[0].strip()

def delete_ami(ami_id):
    ec2_conn = boto.ec2.connect_to_region(aws_region)
    ec2_conn.deregister_image(ami_id, delete_snapshot=True)

def get_groovy_url():
    groovy_url = jenkins_base_url.replace('https://', '');
    if not groovy_url.endswith('/'):
        groovy_url = '%s/' % groovy_url
    return 'https://%s:%s@%sscriptText' % (
            jenkins_auth_user,
            jenkins_auth_password,
            groovy_url)

def get_jenkins_ami_id():
    groovy_url = get_groovy_url()
    groovy_script = """
        def foundAmi = ""
        Jenkins.instance.clouds.each {
          if (it.displayName == '%s') {
            it.getTemplates().each {
              if (it.getDisplayName().toLowerCase().contains("%s".toLowerCase())) {
                // By definition, this will return the last result it finds
                // You better make sure you supply a unique ami_profile_name ;)
                foundAmi = it.getAmi();
              }
            }
          }
        }
        println(foundAmi)
        """ % (ec2_cloud_instance, ami_profile_name)
    payload = {'script': groovy_script}
    r = requests.post(groovy_url, verify=False, data=payload)
    if not r.status_code == 200:
        print 'HTTP POST to Jenkins URL %s resulted in %s' % (groovy_url, r.status_code)
        print r.headers
        print r.text
        sys.exit(1)

    return r.text.strip()

def update_jenkins_ami_id(ami_id):
    groovy_url = get_groovy_url()
    groovy_script = """
        def foundAmi = ""
        Jenkins.instance.clouds.each {
          if (it.displayName == '%s') {
            it.getTemplates().each {
              if (it.getDisplayName().toLowerCase().contains("%s".toLowerCase())) {
                // By definition, this will update all the results it finds
                // You better make sure you supply a unique ami_profile_name ;)
                it.setAmi("%s")
                foundAmi = "yes"
              }
            }
          }
        }
        Jenkins.instance.save()
        println(foundAmi)
        """ % (ec2_cloud_instance, ami_profile_name, ami_id)
    payload = {'script': groovy_script}
    r = requests.post(groovy_url, verify=False, data=payload)
    if not r.status_code == 200:
        print 'HTTP POST to Jenkins URL %s resulted in %s' % (groovy_url, r.status_code)
        print r.headers
        print r.text
        sys.exit(1)

    return r.text.strip() == "yes"

def main():
    # Very high level overview of how this is supposed to work:
    # ---------------------------------------------------------
    # Get the Jenkins build output and check for errors
    #   - If there were errors,
    #       - delete the ami that was created
    #       - fail the build
    #   - If there were no errors,
    #       - Update Jenkins with the newly created AMI ID
    #       - Delete the old AMI in AWS
    #       - Pass the build

    error_lines = get_error_lines(get_jenkins_build_output())
    packer_ami_id = get_packer_ami_id(get_jenkins_build_output())
    if error_lines:
        print error_lines
        print "Deleting newly created AMI %s" % packer_ami_id
        delete_ami(packer_ami_id)
        sys.exit(1)

    old_jenkins_ami_id = get_jenkins_ami_id()
    if not old_jenkins_ami_id:
        print "Could not find (current) Jenkins AMI ID -- moving on"

    update_success = update_jenkins_ami_id(packer_ami_id)
    if not update_success:
        print "Ran into an error when attempting to update the Jenkins AMI ID"
        print "Deleting newly created AMI %s" % packer_ami_id
        delete_ami(packer_ami_id)
        sys.exit(1)

    if old_jenkins_ami_id:
        print "Deleting previous Jenkins AMI %s in AWS" % old_jenkins_ami_id
        delete_ami(old_jenkins_ami_id)

if __name__ == '__main__':
    main()
