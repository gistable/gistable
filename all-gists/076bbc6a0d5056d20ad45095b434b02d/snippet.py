#!/usr/bin/env python
"""
As part of my jenkins build-pipeline, I'm having jenkins build and then deploy my services directly into nomad.
my build and deploy in jenkins looks like this:
docker build -t pdfservice:$BUILD_NUMBER .
docker tag pdfservice:$BUILD_NUMBER registry.service.consul:5000/pdfservice:$BUILD_NUMBER
docker push registry.service.consul:5000/pdfservice:$BUILD_NUMBER
docker build -t pdfservice:latest .
docker tag pdfservice:latest registry.service.consul:5000/pdfservice:latest
docker push registry.service.consul:5000/pdfservice:latest
sed "s/@@BUILD_NUMBER@@/$BUILD_NUMBER/g" pdfservice.nomad.sed >pdfservice.nomad
nomad run pdfservice.nomad
./nomad-check.py pdfservice $BUILD_NUMBER

So, this code nomad-check, will see if the tag BUILD_NUMBER got ran successfully with nomad, if it failed for whatever reason
then it will roll-back to a previous BUILD_NUMBER.  (up to 10 times).

 uses https://github.com/jrxfive/python-nomad
    pip install python-nomad

"""
import subprocess
import sys
import time
import nomad

def job(n, service):
    """
    return a job
    """
    return n.job.get_job(service)

def check(n, service):
    """return status on service with nomad connection n
    """
    s = job(n, service)
    return s[u'Status']

def imageBuildNumber(image):
    """return build number from image config"""
    try:
        return image.rsplit(':', 1)[1]
    except IndexError:
        return 0
    except AttributeError:
        return 0

def rollback(service, buildNumber):
    """rollback nomad service to buildNumber.
    i.e. you give me the buildNumber to go back to.
    """
    sed = 'sed "s/@@BUILD_NUMBER@@/%s/g" pdfservice.nomad.sed >pdfservice.nomad' % buildNumber
    out = subprocess.check_output(sed, shell=True)
    print(sed, out)
    out = subprocess.check_output(['nomad','run','%s.nomad' % service])
    print('nomad:', out)
    return True

def waitForBuildAndThenCheck(n, service, buildNumber, secs=10):
    """wait around until we get the right build number in the image, and then run a check
    """
    for i in range(1, secs):
        s = job(n, service)
        image = s['TaskGroups'][0]['Tasks'][0]['Config']['image']
        iBuildNumber = imageBuildNumber(image)
        if buildNumber == iBuildNumber:
            return True, s[u'Status']
        else:
            time.sleep(1)
    return image, s[u'Status']
def check(n, service, buildNumber):
    """
    check service for buildNumber as running and happy.
    returns True if happy.
    returns False if not happy.
    """
    success, status = waitForBuildAndThenCheck(n, service, buildNumber)
    if success is True:
        if status == 'running':
            print("OK: %s is in %s state with buildNumber %s" % (service, status, buildNumber))
            return True
    print("ERROR: %s is in state %s with buildNumber %s (%s)" % (service, status, imageBuildNumber(success), success))
    return False

def main(service, buildNumber):
    """main"""
    n = nomad.Nomad('nomad.service.consul', timeout=5)
    if check(n, service, buildNumber):
        #success!
        sys.exit(0)
    else:
        # rollback to a previous working build...
        # up to 5 previous builds.
        prevBuildNumber = int(buildNumber)-1
        for i in range(prevBuildNumber, prevBuildNumber-5, -1):
            print("INFO:rolling back to buildnumber:%s" % i)
            prevbuildNumber = str(i)
            rollback(service, i)
            ret = check(n, service, i)
            if ret:
                sys.exit(0)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])