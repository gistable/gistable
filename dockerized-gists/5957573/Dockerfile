FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "shapely"]
RUN ["pip", "install", "geopandas"]
RUN ["pip", "install", "pyproj"]
CMD ["python", "snippet.py"]