FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "descartes"]
RUN ["pip", "install", "matplotlib"]
RUN ["pip", "install", "fiona"]
RUN ["pip", "install", "matplotlib"]
RUN ["pip", "install", "shapely"]
CMD ["python", "snippet.py"]