FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "mpl_toolkits"]
RUN ["pip", "install", "matplotlib"]
RUN ["pip", "install", "numpy"]
RUN ["pip", "install", "pykitti"]
RUN ["pip", "install", "mayavi"]
CMD ["python", "snippet.py"]