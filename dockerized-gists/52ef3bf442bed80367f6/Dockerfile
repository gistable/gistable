FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "mercantile"]
RUN ["pip", "install", "pyproj"]
CMD ["python", "snippet.py"]