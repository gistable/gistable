"""Example of usage of Joblib with Amazon S3."""

import s3io
import joblib
import numpy as np

big_obj = [np.ones((500, 500)), np.random.random((1000, 1000))]

# Customize the following values with yours
bucket = "my-bucket"
key = "my_pickle.pkl"
compress = ('gzip', 3)
credentials = dict(
    aws_access_key_id="<Public Key>",
    aws_secret_access_key="Private Key",
)

# Dump in an S3 file is easy with Joblib
with s3io.open('s3://{0}/{1}'.format(bucket, key), mode='w',
               **credentials) as s3_file:
    joblib.dump(big_obj, s3_file, compress=compress)

with s3io.open('s3://{0}/{1}'.format(bucket, key), mode='r',
               **credentials) as s3_file:
    obj_reloaded = joblib.load(s3_file)

print("Correctly reloaded? {0}".format(all(np.allclose(x, y)
                                           for x, y in zip(big_obj,
                                                           obj_reloaded))))