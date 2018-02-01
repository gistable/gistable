from functools import partial
import numpy as np
from scipy.spatial import cKDTree
from dask.delayed import delayed
import dask.bag as db

class DaskKDTree(object):
    """
    
    Usage Example:
    --------------
    
    from dask.distributed import Client
    client = Client('52.91.203.58:8786')
    tree = DaskKDTree(client, leafsize=1000)
    tree.load_random(num_points=int(1e8), chunk_size=int(1e6))
    
    # find all points within 10km of Bourbon Street
    bourbon_street = (-10026195.958134, 3498018.476606)
    radius = 10000 # meters
    result = tree.query_ball_point(x=bourbon_street, r=radius)
    """
    
    
    def __init__(self, client, leafsize):
        self.client = client
        self.leafsize = leafsize
        self.trees = []
    
    
    def load_random(self, num_points=int(1e6), chunk_size=300):
        parts = int(num_points / chunk_size)
        self.trees = [delayed(DaskKDTree._run_load_random)(int(chunk_size), leafsize=self.leafsize) for f in range(parts)]
        self.trees = self.client.persist(self.trees)
        
        
    @staticmethod
    def _run_load_random(count, leafsize):
        xs = np.random.uniform(int(-20e6), int(20e6), count)
        ys = np.random.uniform(int(-20e6), int(20e6), count)
        points = np.dstack((xs, ys))[0, :]
        return cKDTree(points, leafsize=leafsize)    
    
    
    def query_ball_point(self, **kwargs):
        nearest = [delayed(DaskKDTree._run_query_ball_point)(d, kwargs) for d in self.trees]
        b = db.from_delayed(nearest)
        return b.compute()
    
    
    @staticmethod
    def _run_query_ball_point(tree, query_info):
        indices = tree.query_ball_point(**query_info)
        return tree.data[indices]    