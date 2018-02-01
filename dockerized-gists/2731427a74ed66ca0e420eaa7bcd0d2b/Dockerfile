FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "shapely"]
RUN ["pip", "install", "geopandas"]
RUN ["pip", "install", "fiona"]
RUN ["pip", "install", "pandas"]
CMD ["python", "snippet.py"]