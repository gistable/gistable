FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "tornado"]
RUN ["pip", "install", "rx"]
CMD ["python", "snippet.py"]