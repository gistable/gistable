import botocore
import boto3
import functools
import time


DEFAULT_BACKOFF_COEFF = 50.0
DEFAULT_MAX_ATTEMPTS = 4
MAX_BATCH_SIZE = 25
RETRYABLE_ERRORS = [
    "InternalServerError",
    "ProvisionedThroughputExceededException"
]


def default_backoff_func(operation, attempts):
    '''
    Exponential backoff helper.

    attempts is the number of calls so far that have failed
    '''
    if attempts == DEFAULT_MAX_ATTEMPTS:
        raise RuntimeError("Failed {} after {} attempts".format(
            operation, attempts))
    return (DEFAULT_BACKOFF_COEFF * (2 ** attempts)) / 1000.0


class RetryWrapper(object):
    def __init__(self, backoff_func=None):
        '''

        backoff_func is an optional function with signature
        (operation name, attempts so far) that should either:
            - return the number of seconds to sleep
            - raise to stop
        '''
        self.backoff_func = backoff_func or default_backoff_func

    def __call__(self, func, *args, **kwargs):
        '''
        Uses `self.backoff_func` to handle retries.
        '''
        operation = func.__name__
        attempts = 1
        while True:
            try:
                output = func(*args, **kwargs)
            except botocore.exceptions.ClientError as error:
                error_code = error.response['Error']['Code']
                if error_code not in RETRYABLE_ERRORS:
                    raise error
            else:
                # No exception, success!
                return output

            # Backoff in milliseconds
            # backoff_func will return a number of seconds to wait, or raise
            delay = self.backoff_func(operation, attempts)
            time.sleep(delay)
            attempts += 1


# Sample usage:
with_retries = RetryWrapper(backoff_func=default_backoff_func)

codedeploy = boto3.service('codedeploy')
get_deployment = functools.partial(with_retries, codedeploy.get_deployment)

deployment = get_deployment(deploymentId='string')