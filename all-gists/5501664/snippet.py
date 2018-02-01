import os
import random
import string
import tempfile
import subprocess

def random_id(length=8):
    return ''.join(random.sample(string.ascii_letters + string.digits, length))

TEMPLATE_SERIAL = """
#####################################
#$ -S /bin/bash
#$ -cwd
#$ -N {name}
#$ -e {errfile}
#$ -o {logfile}
#$ -pe make {slots}
#####################################
echo "------------------------------------------------------------------------"
echo "Job started on" `date`
echo "------------------------------------------------------------------------"
{script}
echo "------------------------------------------------------------------------"
echo "Job ended on" `date`
echo "------------------------------------------------------------------------"
"""

def submit_python_code(code, name="job", logfile="output.$JOB_ID", errfile="error.$JOB_ID", cleanup=True, prefix="", slots=1):
    base = prefix + "submit_{0}".format(random_id())
    open(base + '.py', 'wb').write(code)
    script = "python " + base + ".py"
    open(base + '.qsub', 'wb').write(TEMPLATE_SERIAL.format(script=script, name=name, logfile=logfile, errfile=errfile, slots=slots))
    try:
        subprocess.call('qsub < ' + base + '.qsub', shell=True)
    finally:
        if cleanup:
            os.remove(base + '.qsub')