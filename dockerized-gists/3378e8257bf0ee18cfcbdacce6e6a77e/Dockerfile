FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "IPython"]
RUN ["pip", "install", "zmq"]
RUN ["pip", "install", "IPython"]
RUN ["pip", "install", "ipywidgets"]
CMD ["python", "snippet.py"]