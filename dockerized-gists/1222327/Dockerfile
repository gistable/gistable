FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "posix_ipc"]
CMD ["python", "snippet.py"]