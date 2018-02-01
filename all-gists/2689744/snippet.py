def gen_redis_proto(*args):
    proto = ''
    proto += '*' + str(len(args)) + '\r\n'
    for arg in args:
        proto += '$' + str(len(arg)) + '\r\n'
        proto += str(arg) + '\r\n'
    return proto