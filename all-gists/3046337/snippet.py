    p = subprocess.Popen(["ls"], shell=True,
                         stdout=subprocess.PIPE, close_fds=True)

    data = p.communicate()[0]

    if p.returncode:
        sys.stderr.write('Bad exit code from hg\n')
        sys.exit(1)