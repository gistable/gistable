FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "git"]
RUN ["pip", "install", "IPython"]
CMD ["python", "snippet.py"]