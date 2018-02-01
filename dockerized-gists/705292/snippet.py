def local2(command, print_command=False):
    "Run a command, returning the exit code, output, and stderr."
    from subprocess import Popen, PIPE

    p = Popen(command, stdout=PIPE, stderr=PIPE)
    if print_command: print " ".join(command)
    output, errput = p.communicate()
    return p.returncode, output, errput


class NexusRepository(object):
    def __init__(self, hostname, repository=None):
        if repository is None:
            repository = "releases"

        self.hostname = hostname
        self.repository = repository

    def _determine_packaging(self, filename, packaging):
        if packaging is not None:
            return packaging

        if filename.endswith('.tar.gz'):
            return 'tar.gz'

        return os.path.splitext(filename)[1].lstrip('.')

    def upload(self, artifact, sourcefile, packaging=None):
        if artifact.version in [None, 'LATEST']:
            raise Exception("Cannot upload version 'LATEST'.")

        url = "http://%(hostname)s/content/repositories/%(repo)s" % {
            'hostname': self.hostname,
            'repo': self.repository,
        }

        if packaging is None:
            if sourcefile.endswith('.tar.gz'):
                packaging = 'tar.gz'
            else:
                packaging = os.path.splitext(sourcefile)[1].lstrip('.')

        status, stdout, stderr = local2([
            MAVEN_BINARY,
            "deploy:deploy-file",
            "-Durl=" + url,
            "-DrepositoryId=" + self.repository,
            "-Dversion=" + artifact.version,
            "-Dfile=" + sourcefile,
            "-DartifactId=" + artifact.artifact_id,
            "-Dpackaging=" + self._determine_packaging(sourcefile, packaging),
            "-DgroupId=" + artifact.group_id,
        ])
        return status, stdout, stderr

    def download(self, artifact, targetfile=None, packaging=None):
        params = {
            'r': self.repository,
            'g': artifact.group_id,
            'a': artifact.artifact_id,
            'v': artifact.version
        }

        params['e'] = self._determine_packaging(targetfile, packaging)

        if artifact.classifier:
            params['c'] = artifact.classifier

        url = "http://%(hostname)s/service/local/artifact/maven/redirect?%(qs)s" % {
            'hostname': self.hostname,
            'qs': urllib.urlencode(params),
        }

        print "Will try to download from:"
        print url
        curl_args = ["curl", "-sSLA", "fabric-deploy", url]
        if targetfile is not None:
            curl_args.extend(["-o", targetfile])
        else:
            curl_args.append("-O")

        status, stdout, stderr = local2(curl_args)
        return status, stdout, stderr


class NexusArtifact(object):
    def __init__(self, group_id, artifact_id, version=None, classifier=None):
        if version is None:
            version = "LATEST"

        self.group_id = group_id
        self.artifact_id = artifact_id
        self.version = version
        self.classifier = classifier