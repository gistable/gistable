FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "markovify"]
RUN ["pip", "install", "slackclient"]
CMD ["python", "snippet.py"]