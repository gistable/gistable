FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "numpy"]
RUN ["pip", "install", "line_profiler"]
CMD ["python", "snippet.py"]