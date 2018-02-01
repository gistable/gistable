FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "sip"]
RUN ["pip", "install", "PySide"]
RUN ["pip", "install", "matplotlib"]
RUN ["pip", "install", "PyQt4"]
RUN ["pip", "install", "IPython"]
RUN ["pip", "install", "pytest"]
RUN ["pip", "install", "IPython"]
CMD ["python", "snippet.py"]