FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "diff_match_patch"]
RUN ["pip", "install", "operationengine"]
CMD ["python", "snippet.py"]