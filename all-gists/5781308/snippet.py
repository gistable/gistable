from gzip import GzipFile
from io import BytesIO
import urllib2
from uuid import uuid4
import gdal
 
 
def open_http_query(url):
    try:
        request = urllib2.Request(url, 
            headers={"Accept-Encoding": "gzip"})
        response = urllib2.urlopen(request, timeout=30)
        if response.info().get('Content-Encoding') == 'gzip':
            return GzipFile(fileobj=BytesIO(response.read()))
        else:
            return response
    except urllib2.URLError:
        return None
        
        
def open_image(url):
    image_data = open_http_query(url)
    
    if not image_data:
            return None
            
    mmap_name = "/vsimem/"+uuid4().get_hex()
    gdal.FileFromMemBuffer(mmap_name, image_data.read())
    gdal_dataset = gdal.Open(mmap_name)
    image = gdal_dataset.GetRasterBand(1).ReadAsArray()
    gdal_dataset = None
    gdal.Unlink(mmap_name)
    
    return image
