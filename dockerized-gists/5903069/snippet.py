from boto.s3.connection import S3Connection
from progressbar import Percentage, ETA, FileTransferSpeed, Bar, ProgressBar


class S3Transfer(object):
    def __init__(self, aws_key, aws_secret):
        self.conn = S3Connection(aws_key, aws_secret)
        self.progress_bar = None

    def _update_progress_bar(self, bytes_transferred, size):
        self.progress_bar.update(bytes_transferred)

    def get_object(self, bucket_name, object_name, save_to):
        bucket = self.conn.get_bucket(bucket_name)
        key = bucket.get_key(object_name)

        widgets = ['%s/%s: ' % (bucket.name, key.name), Percentage(), ' ', Bar(marker='=',left='[',right=']'),
            ' ', ETA(), ' ', FileTransferSpeed()]
        self.progress_bar = ProgressBar(widgets=widgets, maxval=key.size)
        self.progress_bar.start()
        key.get_contents_to_filename(save_to, cb=self._update_progress_bar, num_cb=10000)
        self.progress_bar.finish()