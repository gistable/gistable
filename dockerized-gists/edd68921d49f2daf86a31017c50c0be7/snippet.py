"""
AWS Batch wrapper for Luigi

From the AWS website:

    AWS Batch enables you to run batch computing workloads on the AWS Cloud. 

    Batch computing is a common way for developers, scientists, and engineers 
    to access large amounts of compute resources, and AWS Batch removes the 
    undifferentiated heavy lifting of configuring and managing the required 
    infrastructure. AWS Batch is similar to traditional batch computing 
    software. This service can efficiently provision resources in response to 
    jobs submitted in order to eliminate capacity constraints, reduce compute 
    costs, and deliver results quickly.

See `AWS Batch User Guide`_ for more details.

To use AWS Batch, you create a jobDefinition JSON that defines a `docker run`_
command, and then submit this JSON to the API to queue up the task. Behind the
scenes, AWS Batch auto-scales a fleet of EC2 Container Service instances, 
monitors the load on these instances, and schedules the jobs.

This `boto3-powered`_ wrapper allows you to create Luigi Tasks to submit Batch
``jobDefinition`` s. You can either pass a dict (mapping directly to the
``jobDefinition`` JSON) OR an Amazon Resource Name (arn) for a previously
registered ``jobDefinition``.

Requires:

- boto3 package
- Amazon AWS credentials discoverable by boto3 (e.g., by using ``aws configure``
  from awscli_)
- An enabled AWS Batch job queue configured to run on a compute environment.

Written and maintained by Jake Feala (@jfeala) for Outlier Bio (@outlierbio)

.. _`docker run`: https://docs.docker.com/reference/commandline/run
.. _jobDefinition: http://http://docs.aws.amazon.com/batch/latest/userguide/job_definitions.html
.. _`boto3-powered`: https://boto3.readthedocs.io
.. _awscli: https://aws.amazon.com/cli
.. _`AWS Batch User Guide`: http://docs.aws.amazon.com/AmazonECS/latest/developerguide/ECS_GetStarted.html

"""

import json
import os
import logging
import random
import string
from subprocess import check_output
import time

import luigi

logger = logging.getLogger('luigi-interface')

try:
    import boto3
    client = boto3.client('batch')

    # Get dict of active queues keyed by name
    queues = {q['jobQueueName']:q for q in client.describe_job_queues()['jobQueues']
              if q['state'] == 'ENABLED' and q['status'] == 'VALID'}
    if not queues:
        logger.warning('No job queues with state=ENABLED and status=VALID')

    # Pick the first queue as default
    DEFAULT_QUEUE_NAME = list(queues.keys())[0]

except ImportError:
    logger.warning('boto3 is not installed. BatchTasks require boto3')


class BatchJobException(Exception):
    pass


POLL_TIME = 10


def random_id():
    return 'luigi-job-' + ''.join(random.sample(string.ascii_lowercase, 8))


def _get_job_status(job_id):
    """
    Retrieve task statuses from ECS API

    Returns list of {SUBMITTED|PENDING|RUNNABLE|STARTING|RUNNING|SUCCEEDED|FAILED} for each id in job_ids
    """
    response = client.describe_jobs(jobs=[job_id])

    # Error checking
    status_code = response['ResponseMetadata']['HTTPStatusCode']
    if status_code != 200:
        msg = 'Job status request received status code {0}:\n{1}'
        raise Exception(msg.format(status_code, response))

    return response['jobs'][0]['status']

def _track_job(job_id):
    """Poll task status until STOPPED"""
    
    while True:
        status = _get_job_status(job_id)
        if status in ['SUCCEEDED', 'FAILED']:
            logger.info('Batch job {0} finished'.format(job_id))
            return status

        time.sleep(POLL_TIME)
        logger.debug('Batch job status for job {0}: {1}'.format(
            job_id, status))


def register_job_definition(json_fpath):
    """Register a job definition with AWS Batch, using a JSON"""
    with open(json_fpath) as f:
        job_def = json.load(f)
    response = client.register_job_definition(**job_def)
    status_code = response['ResponseMetadata']['HTTPStatusCode']
    if status_code != 200:
        msg = 'Register job definition request received status code {0}:\n{1}'
        raise Exception(msg.format(status_code, response))
    return response


class DockerTask(luigi.Task):

    environment = {
        'AWS_ACCESS_KEY_ID': os.environ.get('AWS_ACCESS_KEY_ID'),
        'AWS_SECRET_ACCESS_KEY': os.environ.get('AWS_SECRET_ACCESS_KEY')
    }
    volumes = {'/tmp': '/scratch'}
    image = ''
    command = []

    @property
    def parameters(self):
        """
        Parameters to pass to the command template

        Override to return a dict of key-value pairs to fill in command arguments
        """
        return {}

    def from_job_definition(self):
        pass

    def build_batch_job_definition(self):
        pass

    def _build_command(self):
        def get_param(arg):
            return self.parameters[arg.split('::')[1]]
        return [get_param(arg) if arg.startswith('Ref::') else arg 
                for arg in self.command]

    def build_docker_run(self):
        cmd = ['docker', 'run']
        for name, value in self.environment.items():
            cmd += ['-e', '{}={}'.format(name, value)]
        for host, target in self.volumes.items(): 
            cmd += ['-v', '{}:{}'.format(host, target)]
        
        cmd.append(self.image)

        command = self._build_command()
        cmd += command

        return cmd


class BatchTask(DockerTask):

    """
    Base class for an Amazon Batch job

    Amazon Batch requires you to register "jobs", which are JSON descriptions
    for how to issue the ``docker run`` command. This Luigi Task can either
    run a pre-registered Batch jobDefinition, OR you can register the job on 
    the fly from a Python dict.

    :param job_definition: pre-registered job definition ARN (Amazon Resource
        Name), of the form::

            arn:aws:batch:<region>:<user_id>:job-definition/<job-name>:<version>

    """

    job_definition = luigi.Parameter()
    job_name = luigi.Parameter(default='', significant=False)
    queue_name = luigi.Parameter(default='', significant=False)

    @property
    def batch_job_id(self):
        """Expose the Batch job ID"""
        if hasattr(self, '_job_id'):
            return self._job_id

    def run(self):
        if self.local:
            self.run_local()
            return

        # Use default queue if none specified
        queue_name = self.queue_name or DEFAULT_QUEUE_NAME

        # Get jobId if it already exists
        self._job_id = None
        if self.job_name:
            # Job name is unique. If the job exists, use its id
            jobs = client.list_jobs(jobQueue=queue_name, jobStatus='RUNNING')['jobSummaryList']
            matching_jobs = [job for job in jobs if job['jobName'] == self.job_name]
            if matching_jobs:
                self._job_id = matching_jobs[0]['jobId']


        # Submit the job to AWS Batch if it doesn't exist, get assigned job ID
        if not self._job_id:
            response = client.submit_job(
                jobName = self.job_name or random_id(),
                jobQueue = queue_name,
                jobDefinition = self.job_definition,
                parameters = self.parameters
            )
            self._job_id = response['jobId']

        # Wait on job completion
        status = _track_job(self._job_id)

        # Raise and notify if job failed
        if status == 'FAILED':
            data = client.describe_jobs(jobs=[self._job_id])['jobs']
            raise BatchJobException('Job {}: {}'.format(self._job_id, json.dumps(data, indent=4)))

    def run_local(self):
        cmd = self.build_docker_run()
        logger.info('Running local Docker command:\n{}'.format(' '.join(cmd)))
        out = check_output(cmd)
        logger.info(out.decode())


