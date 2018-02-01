# Python logger in AWS Lambda has a preset format. To change the format of the logging statement, 
# remove the logging handler & add a new handler with the required format

import logging
import sys

def setup_logging():
    logger = logging.getLogger()
    for h in logger.handlers:
      logger.removeHandler(h)
    
    h = logging.StreamHandler(sys.stdout)
    
    # use whatever format you want here
    FORMAT = '%(asctime)s %(message)s'
    h.setFormatter(logging.Formatter(FORMAT))
    logger.addHandler(h)
    logger.setLevel(logging.INFO)
    
    return logger

def lambda_handler(event, context):
    logger = setup_logging()
    logger.info("This is a test log statement!")
    return
    
# Expected output from Lambda:
# 
# START RequestId: 1a2b3c4d-abcd-1234-efgh-1a2b3c4d5e6f Version: $LATEST
# 2017-10-06 22:40:59,653 This is a test log statement!
# END RequestId: 1a2b3c4d-abcd-1234-efgh-1a2b3c4d5e6f
# REPORT RequestId: 1a2b3c4d-abcd-1234-efgh-1a2b3c4d5e6f	Duration: 0.41 ms	Billed Duration: 100 ms 	Memory Size: 128 MB	Max Memory Used: 21 MB
