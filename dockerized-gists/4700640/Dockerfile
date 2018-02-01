FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "bitarray"]
RUN ["pip", "install", "mmh3"]
CMD ["python", "snippet.py"]