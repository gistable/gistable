FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "numba"]
RUN ["pip", "install", "pylab"]
RUN ["pip", "install", "numpy"]
RUN ["pip", "install", "matplotlib"]
RUN ["pip", "install", "matplotlib"]
CMD ["python", "snippet.py"]