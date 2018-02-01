from boto.emr.connection import EmrConnection
from boto.emr.step import InstallPigStep, PigStep

AWS_ACCESS_KEY = '' # REQUIRED
AWS_SECRET_KEY = '' # REQUIRED
conn = EmrConnection(AWS_ACCESS_KEY, AWS_SECRET_KEY)

pig_file = 's3://elasticmapreduce/samples/pig-apache/do-reports2.pig'
INPUT = 's3://elasticmapreduce/samples/pig-apache/input/access_log_1'
OUTPUT = '' # REQUIRED, S3 bucket for job output

pig_args = ['-p', 'INPUT=%s' % INPUT,
            '-p', 'OUTPUT=%s' % OUTPUT]
pig_step = PigStep('Process Reports', pig_file, pig_args=pig_args)
steps = [InstallPigStep(), pig_step]

conn.run_jobflow(name='report test', steps=steps,
                 hadoop_version='0.20.205', ami_version='latest',
                 num_instances=2, keep_alive=False)
