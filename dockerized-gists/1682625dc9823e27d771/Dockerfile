FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "IPython"]
RUN ["pip", "install", "pydot"]
CMD ["python", "snippet.py"]