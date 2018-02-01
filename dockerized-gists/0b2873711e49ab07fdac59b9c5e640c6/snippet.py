def session_test(session):
    session.interpreter = 'python2.7'
    session.install('-e', '.[grpc]')
    session.install('pytest')
    session.run('pytest', '-x', 'google')