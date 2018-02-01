FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "matplotlib"]
RUN ["pip", "install", "simplejson"]
RUN ["pip", "install", "nltk"]
RUN ["pip", "install", "networkx"]
RUN ["pip", "install", "numpy"]
RUN ["pip", "install", "nltk"]
CMD ["python", "snippet.py"]