FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "requests"]
RUN ["pip", "install", "pandas"]
RUN ["pip", "install", "geojson"]
CMD ["python", "snippet.py"]