FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "matplotlib"]
RUN ["pip", "install", "pylab"]
RUN ["pip", "install", "email"]
CMD ["python", "snippet.py"]