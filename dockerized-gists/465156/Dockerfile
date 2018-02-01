FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "shapely"]
RUN ["pip", "install", "matplotlib"]
CMD ["python", "snippet.py"]