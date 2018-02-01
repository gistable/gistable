FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "fritzconnection"]
RUN ["pip", "install", "telepot"]
CMD ["python", "snippet.py"]