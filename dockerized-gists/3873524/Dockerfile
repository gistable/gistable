FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "bitarray"]
RUN ["pip", "install", "smhasher"]
CMD ["python", "snippet.py"]