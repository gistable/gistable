import numpy as np
import rasterio as rio
import dask
import dask.array as da

class RioDataset():
    def __init__(self, filepath, band=1):
        self.band = band
        self.dataset = rio.open(filepath)
        self.dtype = self.dataset.dtypes[band-1]
        self.shape = self.dataset.shape

    def __getitem__(self, val):
        if isinstance(val, tuple):
            try:
                window = []
                for obj in val:
                    if isinstance(obj,slice):
                        assert obj.step in [1, None]
                        window.append((obj.start, obj.stop))
                    elif isinstance(obj, int):
                        window.append((obj, obj+1))
                    else:
                        raise TypeError('Invalid slice')

                return self.dataset.read(self.band, window=window)

            except AssertionError:
                raise TypeError('Invalid slice')
        else:
            raise TypeError('Invalid slice')

class RioArray(da.Array):
    def __init__(self, filepath, band=1):
        self.dataset = rio.open(filepath)
        blocks = list(self.dataset.block_windows())
        block_shape = self.dataset.block_shapes[band-1]
        chunks = block_shape
        dask = {(filepath,ji[0],ji[1]):
                   (self.dataset.read, band, None, window)
                   for ji, window in blocks
               }

        name = filepath
        dtype = self.dataset.dtypes[band-1]
        shape = self.dataset.shape

        da.Array.__init__(self, dask, name, chunks, dtype, shape)


    def __del__(self):
        try:
            self._dataset.close()
            del self._dataset
        except:pass
