# -*- coding: utf-8 -*-

import argparse
import glob
import logging
import os
import re
import subprocess
import time
from multiprocessing import (
    cpu_count,
    Pool
)
from threading import Thread

from boto.elastictranscoder import connect_to_region
from boto.s3.connection import S3Connection
from boto.s3.multipart import MultiPartUpload
from boto.s3.key import Key

logging.basicConfig(level=logging.INFO,
                    format=u'[%(levelname)s/%(processName)s] %(message)s')


def multipart_upload((access_id, access_secret, bucket_name, key_name,
                      mp_id, i, part)):
    connection = S3Connection(access_id, access_secret)
    bucket = connection.get_bucket(bucket_name)
    mp = MultiPartUpload(bucket)
    mp.key_name = key_name
    mp.id = mp_id

    with open(part) as fp:
        mp.upload_part_from_file(fp, i + 1)
    os.remove(part)


class Uploader(object):

    def __init__(self, bucket_name, access_id, access_secret,
                 pattern, ignore_pattern=None):
        self.connection = S3Connection(access_id, access_secret)
        self.bucket = self.connection.get_bucket(bucket_name)
        self.pattern = pattern
        self.ignore_pattern = ignore_pattern

    def get_savepath(self, filepath):
        assert isinstance(filepath, unicode)

        abs_curdir = unicode(os.path.abspath(os.path.curdir))
        abs_filepath = filepath if os.path.isabs(filepath)\
            else os.path.abspath(filepath)

        if abs_filepath.startswith(abs_curdir):
            return abs_filepath[len(abs_curdir) + 1:]
        else:
            raise ValueError

    def upload(self, filepath):
        assert isinstance(filepath, unicode)

        if not os.path.isfile(filepath)\
                or self.pattern.search(filepath) is None\
                or (self.ignore_pattern
                    and self.ignore_pattern.search(filepath)):
            logging.info(u'%s をスキップ' % filepath)
            return False

        savepath = self.get_savepath(filepath)

        if savepath in self.bucket:
            logging.info(u'すでに存在するため %s をスキップ' % filepath)
        else:
            size_mb = os.path.getsize(filepath) / 1e6
            if size_mb < 60:
                logging.info(
                    u'%s をアップロード(保存先: %s)' % (filepath, savepath)
                )
                key = Key(self.bucket)
                key.name = savepath
                key.set_contents_from_filename(filepath)
            else:
                logging.info(
                    u'%s をマルチパートアップロード(保存先: %s)' % (filepath, savepath)
                )
                cores = cpu_count() * 2
                mp = self.bucket.initiate_multipart_upload(savepath)

                pool = Pool(cores)
                pool.map(multipart_upload, (
                    (
                        self.connection.gs_access_key_id,
                        self.connection.gs_secret_access_key,
                        mp.bucket_name, mp.key_name,
                        mp.id, i, part
                    ) for i, part in enumerate(
                        self._split_file(filepath, size_mb, cores)
                    )
                ))
                pool.close()
                pool.join()

                mp.complete_upload()

        return savepath

    def _split_file(self, filepath, size_mb, split_count):
        prefix = os.path.join(os.path.dirname(filepath),
                              u'%sS3PART' % os.path.basename(filepath))
        split_size = int(min(size_mb / split_count, 250))

        if not os.path.exists(u'%saa' % prefix):
            subprocess.check_call(
                [u'split', u'-b%sm' % split_size, filepath, prefix]
            )

        return sorted(glob.glob(u'%s*' % prefix))

    def upload_dir(self, dirname, uploaded=[]):
        for filename in os.listdir(dirname):
            if filename == u'$RECYCLE.BIN':
                continue

            try:
                filepath = os.path.join(dirname, filename)
                if os.path.isfile(filepath):
                    uploaded.append(self.upload(filepath))
                elif os.path.isdir(filepath):
                    self.upload_dir(filepath, uploaded)
            except OSError:
                continue
        else:
            return uploaded


class Downloader(object):

    def __init__(self, bucket_name, access_id, access_secret):
        self.connection = S3Connection(access_id, access_secret)
        self.bucket = self.connection.get_bucket(bucket_name)

    def download(self, key, delete=False):
        if isinstance(key, unicode):
            key = self.bucket.get_key(key)
            if key is None:
                raise ValueError

        savepath = self.get_savepath(key.name)
        logging.info(u'%s のダウンロードを開始 (保存先: %s)' % (
            key.name, savepath
        ))
        key.get_contents_to_filename(savepath)
        logging.info(u'%s のダウンロードを完了' % key.name)

        if delete:
            logging.info(u'%s を削除' % key.name)
            key.delete()

        return savepath

    def download_all(self):
        downloaded = []
        for key in self.bucket:
            downloaded.append(self.download(key))

        return downloaded

    def get_savepath(self, key_name):
        return os.path.join(os.path.abspath(os.curdir), key_name)


class Transcoder(object):

    def __init__(self, region_name, access_id, access_secret):
        self.connection = connect_to_region(
            region_name,
            aws_access_key_id=access_id, aws_secret_access_key=access_secret
        )
        self.pipeline = None
        self.on_finish = lambda status, input_key, output_key: None
        self.jobs = []

        self._access_id = access_id
        self._access_secret = access_secret

        self._progressing = True
        self.__thread = Thread(target=self.__monitor_jobs)
        self.__thread.setDaemon(True)
        self.__thread.start()

    def set_finish_listener(self, listener):
        self.on_finish = listener

    def is_progressings(self):
        return self._progressing and len(self.jobs) > 0

    def select_pipeline(self, pipeline_name):
        pipelines = filter(lambda x: x[u'Name'] == pipeline_name,
                           self.connection.list_pipelines()[u'Pipelines'])
        if len(pipelines) is not 1:
            raise ValueError(u'Bucket(%s) does not exist' % pipeline_name)

        self.pipeline = pipelines[0]

    def get_input_bucket(self):
        assert isinstance(self.pipeline, dict)

        return self.pipeline[u'InputBucket']

    def get_output_bucket(self):
        assert isinstance(self.pipeline, dict)

        return self.pipeline[u'OutputBucket']

    def transcode(self, input_name):
        assert isinstance(self.pipeline, dict)
        output_name = self._get_savepath(input_name)

        logging.info(u'%s の変換ジョブを追加(保存先: %s)' % (
            input_name, output_name
        ))
        response = self.connection.create_job(
            self.pipeline[u'Id'],
            self._get_input_dict(input_name),
            self._get_output_dict(output_name)
        )

        self.jobs.append((response[u'Job'][u'Id'],
                          response[u'Job'][u'Input'][u'Key'],
                          response[u'Job'][u'Output'][u'Key']))
        return self.jobs[-1]

    def _get_savepath(self, input_path):
        connection = S3Connection(self._access_id, self._access_secret)
        bucket = connection.get_bucket(self.get_output_bucket())

        basename = os.path.splitext(input_path)[0]
        x = 0
        while True:
            savepath = u'%s.mp4' % (
                basename if x is 0 else u'%s(%d)' % (basename, x)
            )
            if savepath in bucket:
                x += 1
            else:
                break

        return savepath

    def _get_input_dict(self, input_name):
        return {
            u'Key': input_name,
            u'FrameRate': u'auto',
            u'Resolution': u'auto',
            u'AspectRatio': u'auto',
            u'Interlaced': u'auto',
            u'Container': u'auto'
        }

    def _get_output_dict(self, output_name):
        return {
            u'Key': output_name,
            u'ThumbnailPattern': u'',
            u'Rotate': u'0',
            u'PresetId': u'1351620000000-000001'
        }

    def __monitor_jobs(self):
        while self._progressing:
            for job in self.jobs:
                response = self.connection.read_job(job[0])
                status = response[u'Job'][u'Output'][u'Status']
                if status in (u'Complete', u'Canceled', u'Error'):
                    self.on_finish(status, job[1], job[2])
                    self.jobs.remove(job)
            else:
                time.sleep(10)

    def __del__(self):
        self._progressing = False
        self.__thread.join()


def get_transcoded_listener(bucket, access_id, access_secret):
    downloader = Downloader(bucket, access_id, access_secret)

    def listener(status, input_key, output_key):
        if status == u'Complete':
            logging.info(u'Transcoding of %s was completed' % input_key)
            downloader.download(output_key, delete=True)
        elif status == u'Canceled':
            logging.info(u'Transcoding of %s was canceled' % input_key)
        elif status == u'Error':
            logging.error(u'Transcoding of %s raised error' % input_key)
    return listener


def get_args():
    parser = argparse.ArgumentParser(
        description=u'カレントディレクトリにあるビデオを ElasticTranscoder で'
                    + u' 1080p の mp4 に変換するマン'
    )
    parser.add_argument(
        u'--region',
        help=u'Region name of ElasticTranscoder you want to use',
        required=True
    )
    parser.add_argument(
        u'--pipeline',
        help=u'Name of ElasticTranscoder\'s pipeline you want to use',
        required=True
    )
    parser.add_argument(u'--access_id', help=u'aws_access_key_id',
                        required=True)
    parser.add_argument(u'--access_secret', help=u'aws_secret_access_key',
                        required=True)
    parser.add_argument(u'--pattern', default=ur'.+\.ts$')
    parser.add_argument(u'--ignore_pattern', default=None)

    return parser.parse_args()


def main():
    args = get_args()

    transcoder = Transcoder(args.region, args.access_id, args.access_secret)
    transcoder.select_pipeline(args.pipeline)
    transcoder.set_finish_listener(get_transcoded_listener(
        transcoder.get_output_bucket(), args.access_id, args.access_secret
    ))

    uploader = Uploader(transcoder.get_input_bucket(),
                        args.access_id, args.access_secret,
                        re.compile(args.pattern, re.UNICODE | re.IGNORECASE),
                        args.ignore_pattern and re.compile(
                            args.ignore_pattern, re.UNICODE | re.IGNORECASE
                        ))
    for filepath in uploader.upload_dir(u'.'):
        transcoder.transcode(filepath)

    while transcoder.is_progressings():
        time.sleep(1)


if __name__ == u'__main__':
    main()
