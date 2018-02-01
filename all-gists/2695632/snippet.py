from fabric.api import *
from fabric.operations import local,put
import subprocess
import os

@task
def deploy_small_ec2_instance():
        local('/usr/bin/ec2-run-instances ami-6dacf728 --instance-type m1.small --region us-west-1 --key ${EC2_KEYPAIR} --user-data-file user-data.sh --group ${SGROUP}')

@task
def deploy_medium_ec2_instance():
        local('/usr/bin/ec2-run-instances ami-6dacf728 --instance-type c1.medium --region us-west-1 --key ${EC2_KEYPAIR} --user-data-file user-data.sh --group ${SGROUP}')

@task
def deploy_large_ec2_instance():
        local('/usr/bin/ec2-run-instances ami-6dacf728 --instance-type m1.large --region us-west-1 --key ${EC2_KEYPAIR} --user-data-file user-data.sh --group ${SGROUP}')

@task
def deploy_large_ec2_instance():
        local('/usr/bin/ec2-run-instances ami-6dacf728 --instance-type m1.large --region us-west-1 --key ${EC2_KEYPAIR} --user-data-file user-data.sh --group ${SGROUP}')

