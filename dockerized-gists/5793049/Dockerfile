FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "pynzb"]
RUN ["pip", "install", "par2ools"]
RUN ["pip", "install", "xml"]
CMD ["python", "snippet.py"]