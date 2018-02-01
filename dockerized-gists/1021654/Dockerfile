FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "mpmath"]
RUN ["pip", "install", "numpy"]
CMD ["python", "snippet.py"]