from multiprocessing.dummy import Pool
from urllib3 import HTTPConnectionPool
from tqdm import tqdm
import itertools
import os
import errno

n_connections = 32
domain = 'geo-samples.beatport.com'
http_pool = HTTPConnectionPool(domain)

total_tracks = 4106
stems_per_track = 5
identifiers = list(itertools.product(
    range(1, total_tracks + 1),
    range(0, stems_per_track)))

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def download(url, fn):
    if not os.path.isfile(fn):
        r = http_pool.urlopen('GET', url)
        with open(fn, 'wb') as f:
            if r.status == 200:
                f.write(r.data)
            elif r.status != 404:
                print 'Error: ' + r.status

pbar = tqdm(total=len(identifiers), leave=True)
def job(identifier):
    track_id = str(identifier[0])
    stem_id = str(identifier[1])
    dir_name = os.path.join('stems', track_id)
    track_fn = os.path.join(dir_name, stem_id + '.mp3')
    track_url = '/stems/%s.%s.mp3' % (track_id, stem_id)
    mkdir_p(dir_name)
    download(track_url, track_fn)
    pbar.update(1)

pool = Pool(n_connections)
pool.map(job, identifiers)