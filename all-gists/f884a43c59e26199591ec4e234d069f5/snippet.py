# -*- coding: utf-8 -*-
# /var/runtime/awslambda/bootstrap.py
"""
aws_lambda.bootstrap.py
Amazon Lambda

Copyright (c) 2013 Amazon. All rights reserved.

Lambda runtime implemention
"""
from __future__ import print_function

import decimal
import imp
import json
import logging
import os
import site
import socket
import sys
import time
import traceback

import runtime as lambda_runtime

import wsgi


def _get_handlers(handler, mode):
    lambda_runtime.report_user_init_start()
    init_handler = lambda: None

    """
    This is the old way we were loading modules.
    It was causing intermittent build failures for unknown reasons.
    Using the imp module seems to remove these failures.
    The imp module appears to be more extreme in that it reloads
    the module if it is already loaded, and it likely doesn't use any caches when
    searching for the module but does a full directory search, which is what we want.
    """
    # m = imp.load_module(modname, globals(), locals(), [])

    try:
        (modname, fname) = handler.rsplit('.', 1)
    except ValueError as e:
        fault = wsgi.FaultException("Bad handler '{}'".format(handler), str(e), None)
        request_handler = make_fault_handler(fault)
        lambda_runtime.report_user_init_end()
        return init_handler, request_handler

    file_handle, pathname, desc = None, None, None
    try:
        # Recursively loading handler in nested directories
        for segment in modname.split('.'):
            if pathname is not None:
                pathname = [pathname]
            file_handle, pathname, desc = imp.find_module(segment, pathname)
        if file_handle is None:
            module_type = desc[2]
            if module_type == imp.C_BUILTIN:
                request_handler = make_fault_handler(wsgi.FaultException(
                    "Cannot use built-in module {} as a handler module".format(modname),
                    None,
                    None
                ))
                lambda_runtime.report_user_init_end()
                return init_handler, request_handler
        m = imp.load_module(modname, file_handle, pathname, desc)
    except Exception as e:
        request_handler = load_handler_failed_handler(e, modname)
        lambda_runtime.report_user_init_end()
        return init_handler, request_handler
    finally:
        if file_handle is not None:
            file_handle.close()

    try:
        init_handler = getattr(m, 'init')
    except AttributeError as e:
        pass

    try:
        request_handler = make_final_handler(getattr(m, fname), mode)
    except AttributeError as e:
        fault = wsgi.FaultException("Handler '{}' missing on module '{}'".format(fname, modname), str(e), None)
        request_handler = make_fault_handler(fault)
    lambda_runtime.report_user_init_end()
    return init_handler, request_handler


# Run a function called 'init', if provided in the same module as the request handler. This is an
# undocumented feature, existed to keep backward compatibility.
def run_init_handler(init_handler, invokeid):
    try:
        init_handler()
    except wsgi.FaultException as e:
        lambda_runtime.report_fault(invokeid, e.msg, e.except_value, e.trace)


class number_str(float):
    def __init__(self, o):
        self.o = o

    def __repr__(self):
        return str(self.o)


def decimal_serializer(o):
    if isinstance(o, decimal.Decimal):
        return number_str(o)
    raise TypeError(repr(o) + " is not JSON serializable")


def load_handler_failed_handler(e, modname):
    if isinstance(e, ImportError):
        return make_fault_handler(wsgi.FaultException("Unable to import module '{}'".format(modname), str(e), None))
    elif isinstance(e, SyntaxError):
        trace = "File \"%s\" Line %s\n\t%s" % (e.filename, e.lineno, e.text)
        fault = wsgi.FaultException("Syntax error in module '{}'".format(modname), str(e), trace)
    else:
        exc_info = sys.exc_info()
        trace = traceback.format_list(traceback.extract_tb(exc_info[2]))
        fault = wsgi.FaultException("module initialization error", str(e), trace[1:])
    return make_fault_handler(fault)


def make_fault_handler(fault):
    def result(*args):
        raise fault

    return result


def set_environ(credentials):
    key, secret, session = credentials.get('key'), credentials.get('secret'), credentials.get('session')
    # TODO delete from environ if params not found
    if credentials.get('key'):
        os.environ['AWS_ACCESS_KEY_ID'] = key
    if credentials.get('secret'):
        os.environ['AWS_SECRET_ACCESS_KEY'] = secret
    if credentials.get('session'):
        os.environ['AWS_SESSION_TOKEN'] = session
        os.environ['AWS_SECURITY_TOKEN'] = session


'''
PYTHONPATH may have paths that were not available when the interpreter was launched.
This would force the path importer cache get updated.
'''


def force_path_importer_cache_update():
    for path in os.environ.get("PYTHONPATH", "").split(":"):
        if path == os.environ["LAMBDA_RUNTIME_DIR"]:
            continue
        importer = sys.path_importer_cache.get(path, None)
        if not importer or isinstance(importer, imp.NullImporter):
            sys.path_importer_cache.pop(path, None)


def wait_for_start():
    (invokeid, mode, handler, suppress_init, credentials) = lambda_runtime.receive_start()
    force_path_importer_cache_update()
    set_environ(credentials)
    lambda_runtime.report_running(invokeid)

    return (invokeid, mode, handler, suppress_init, credentials)


def wait_for_invoke():
    (
        invokeid,
        data_sock,
        credentials,
        event_body,
        context_objs,
        invoked_function_arn,
        x_amzn_trace_id
    ) = lambda_runtime.receive_invoke()

    set_environ(credentials)

    return (invokeid, x_amzn_trace_id, data_sock, credentials, event_body, context_objs, invoked_function_arn)


def make_final_handler(handlerfn, mode):
    if mode == "http":
        def result(sockfd):
            invoke_http(handlerfn, sockfd)
    elif mode == "event":
        return handlerfn
    else:
        def result(sockfd):
            raise wsgi.FaultException("specified mode is invalid: " + mode)
    return result


def invoke_http(handlerfn, sockfd):
    fault_data = wsgi.handle_one(sockfd, ('localhost', 80), handlerfn)
    if fault_data:
        raise wsgi.FaultException(fault_data.msg, fault_data.except_value, fault_data.trace)


def try_or_raise(function, error_message):
    try:
        return function()
    except Exception as e:
        raise JsonError(sys.exc_info(), error_message)


def make_error(errorMessage, errorType, stackTrace):  # stackTrace is an array
    result = {}
    if errorMessage:
        result['errorMessage'] = errorMessage
    if errorType:
        result['errorType'] = errorType
    if stackTrace:
        result['stackTrace'] = stackTrace
    return result


def handle_http_request(request_handler, invokeid, sockfd):
    try:
        request_handler(sockfd)
    except wsgi.FaultException as e:
        lambda_runtime.report_fault(invokeid, e.msg, e.except_value, e.trace)
    finally:
        try:
            os.close(sockfd)
        except Exception as e:
            print("Error closing original data connection descriptor", file=sys.stderr)
            traceback.print_exc()
        finally:
            lambda_runtime.report_done(invokeid, None, None)


def to_json(obj):
    return json.dumps(obj, default=decimal_serializer)


def handle_event_request(request_handler, invokeid, event_body, context_objs, invoked_function_arn):
    lambda_runtime.report_user_invoke_start()
    errortype = None
    try:
        client_context = context_objs.get('client_context')
        if client_context:
            client_context = try_or_raise(lambda: json.loads(client_context), "Unable to parse client context")
        context = LambdaContext(invokeid, context_objs, client_context, invoked_function_arn)
        json_input = try_or_raise(lambda: json.loads(event_body), "Unable to parse input as json")
        result = request_handler(json_input, context)
        result = try_or_raise(lambda: to_json(result), "An error occurred during JSON serialization of response")
    except wsgi.FaultException as e:
        lambda_runtime.report_fault(invokeid, e.msg, e.except_value, None)
        report_xray_fault_helper("LambdaValidationError", e.msg, [])
        result = make_error(e.msg, None, None)
        result = to_json(result)
        errortype = "unhandled"
    except JsonError as e:
        result = report_fault_helper(invokeid, e.exc_info, e.msg)
        result = to_json(result)
        errortype = "unhandled"
    except Exception as e:
        result = report_fault_helper(invokeid, sys.exc_info(), None)
        result = to_json(result)
        errortype = "unhandled"
    lambda_runtime.report_user_invoke_end()
    lambda_runtime.report_done(invokeid, errortype, result)


def craft_xray_fault(ex_type, ex_msg, working_dir, tb_tuples):
    stack = []
    files = set()
    for t in tb_tuples:
        tb_file, tb_line, tb_method, tb_code = t
        tb_xray = {
            'label': tb_method,
            'path': tb_file,
            'line': tb_line
        }
        stack.append(tb_xray)
        files.add(tb_file)

    formatted_ex = {
        'message': ex_msg,
        'type': ex_type,
        'stack': stack
    }
    xray_fault = {
        'working_directory': working_dir,
        'exceptions': [formatted_ex],
        'paths': list(files)
    }
    return xray_fault


def report_xray_fault_helper(etype, msg, tb_tuples):
    xray_fault = craft_xray_fault(etype, msg, os.getcwd(), tb_tuples)
    xray_json = to_json(xray_fault)
    try:
        lambda_runtime.report_xray_exception(xray_json)
    except:
        # Intentionally swallowing
        # We don't report exception to the user just because Xray reported an exception.
        pass


def report_fault_helper(invokeid, exc_info, msg):
    etype, value, tb = exc_info
    if msg:
        msgs = [msg, str(value)]
    else:
        msgs = [str(value), etype.__name__]

    tb_tuples = extract_traceback(tb)

    if sys.version_info[0] >= 3:
        awesome_range = range
    else:
        awesome_range = xrange

    for i in awesome_range(len(tb_tuples)):
        if "/bootstrap.py" not in tb_tuples[i][0]:  # filename of the tb tuple
            tb_tuples = tb_tuples[i:]
            break

    lambda_runtime.report_fault(
        invokeid,
        msgs[0],
        msgs[1],
        (
            "Traceback (most recent call last):\n"
            + ''.join(traceback.format_list(tb_tuples))
            + ''.join(traceback.format_exception_only(etype, value))
        )
    )
    report_xray_fault_helper(etype.__name__, msgs[0], tb_tuples)

    return make_error(str(value), etype.__name__, tb_tuples)


def extract_traceback(tb):
    frames = traceback.extract_tb(tb)

    if sys.version_info[0] >= 3:
        # Python3 returns a list of SummaryFrames instead of a list of tuples
        # for traceback.extract_tb() calls.
        # To make it consistent, we map the list of frames to a list of tuples just like python2
        frames = [(frame.filename, frame.lineno, frame.name, frame.line) for frame in frames]

    return frames


class CustomFile(object):
    def __init__(self, fd):
        self._fd = fd

    def __getattr__(self, attr):
        return getattr(self._fd, attr)

    def write(self, msg):
        lambda_runtime.log_bytes(msg, self._fd.fileno())
        self._fd.flush()

    def writelines(self, msgs):
        for msg in msgs:
            lambda_runtime.log_bytes(msg, self._fd.fileno())
            self._fd.flush()


class CognitoIdentity(object):
    __slots__ = ["cognito_identity_id", "cognito_identity_pool_id"]


class Client(object):
    __slots__ = ["installation_id", "app_title", "app_version_name", "app_version_code", "app_package_name"]


class ClientContext(object):
    __slots__ = ['custom', 'env', 'client']


def make_obj_from_dict(_class, _dict, fields=None):
    if _dict is None:
        return None
    obj = _class()
    set_obj_from_dict(obj, _dict)
    return obj


def set_obj_from_dict(obj, _dict, fields=None):
    if fields is None:
        fields = obj.__class__.__slots__
    for field in fields:
        setattr(obj, field, _dict.get(field, None))


class LambdaContext(object):
    def __init__(self, invokeid, context_objs, client_context, invoked_function_arn=None):
        self.aws_request_id = invokeid
        self.log_group_name = os.environ['AWS_LAMBDA_LOG_GROUP_NAME']
        self.log_stream_name = os.environ['AWS_LAMBDA_LOG_STREAM_NAME']
        self.function_name = os.environ["AWS_LAMBDA_FUNCTION_NAME"]
        self.memory_limit_in_mb = os.environ['AWS_LAMBDA_FUNCTION_MEMORY_SIZE']
        self.function_version = os.environ['AWS_LAMBDA_FUNCTION_VERSION']
        self.invoked_function_arn = invoked_function_arn

        self.client_context = make_obj_from_dict(ClientContext, client_context)
        if self.client_context is not None:
            self.client_context.client = make_obj_from_dict(Client, self.client_context.client)
        self.identity = make_obj_from_dict(CognitoIdentity, context_objs)

    def get_remaining_time_in_millis(self):
        return lambda_runtime.get_remaining_time()

    def log(self, msg):
        lambda_runtime.send_console_message(str(msg))


class LambdaLoggerHandler(logging.Handler):
    def __init__(self):
        logging.Handler.__init__(self)

    def emit(self, record):
        lambda_runtime.send_console_message(self.format(record))


class LambdaLoggerFilter(logging.Filter):
    def filter(self, record):
        record.aws_request_id = _GLOBAL_AWS_REQUEST_ID or ""
        return True


class JsonError(Exception):
    def __init__(self, exc_info, msg):
        self.exc_info = exc_info
        self.msg = msg


_GLOBAL_DEFAULT_TIMEOUT = socket._GLOBAL_DEFAULT_TIMEOUT
_GLOBAL_AWS_REQUEST_ID = None


def log_info(msg):
    lambda_runtime.log_sb("[INFO] ({}) {}".format(__file__, msg))


def main():
    if sys.version_info[0] < 3:
        reload(sys)
        sys.setdefaultencoding('utf-8')

    sys.stdout = CustomFile(sys.stdout)
    sys.stderr = CustomFile(sys.stderr)

    logging.Formatter.converter = time.gmtime
    logger = logging.getLogger()
    logger_handler = LambdaLoggerHandler()
    logger_handler.setFormatter(logging.Formatter(
        '[%(levelname)s]\t%(asctime)s.%(msecs)dZ\t%(aws_request_id)s\t%(message)s\n',
        '%Y-%m-%dT%H:%M:%S'
    ))
    logger_handler.addFilter(LambdaLoggerFilter())
    logger.addHandler(logger_handler)

    global _GLOBAL_AWS_REQUEST_ID

    # Remove lambda internal environment variables
    for env in [
        "_LAMBDA_CONTROL_SOCKET",
        "_LAMBDA_SHARED_MEM_FD",
        "_LAMBDA_LOG_FD",
        "_LAMBDA_CONSOLE_SOCKET",
        "_LAMBDA_RUNTIME_LOAD_TIME"
    ]:
        del os.environ[env]

    (invokeid, mode, handler, suppress_init, credentials) = wait_for_start()

    sys.path.insert(0, os.environ['LAMBDA_TASK_ROOT'])

    # Set /var/task as site directory so we are able to load all customer pth files
    if sys.version_info[0] >= 3:
        site.addsitedir(os.environ["LAMBDA_TASK_ROOT"])

    if suppress_init:
        init_handler, request_handler = lambda: None, None
    else:
        init_handler, request_handler = _get_handlers(handler, mode)
    run_init_handler(init_handler, invokeid)
    lambda_runtime.report_done(invokeid, None, None)
    log_info("init complete at epoch {0}".format(int(round(time.time() * 1000))))

    while True:
        (invokeid, x_amzn_trace_id, sockfd, credentials, event_body, context_objs, invoked_function_arn) = wait_for_invoke()
        _GLOBAL_AWS_REQUEST_ID = invokeid

        if x_amzn_trace_id != None:
            os.environ['_X_AMZN_TRACE_ID'] = x_amzn_trace_id
        elif '_X_AMZN_TRACE_ID' in os.environ:
            del os.environ['_X_AMZN_TRACE_ID']

        # If the handler hasn't been loaded yet, due to init suppression, load it now.
        if request_handler is None:
            init_handler, request_handler = _get_handlers(handler, mode)
            run_init_handler(init_handler, invokeid)

        if mode == "http":
            handle_http_request(request_handler, invokeid, sockfd)
        elif mode == "event":
            handle_event_request(request_handler, invokeid, event_body, context_objs, invoked_function_arn)


if __name__ == '__main__':
    log_info("main started at epoch {0}".format(int(round(time.time() * 1000))))
    main()