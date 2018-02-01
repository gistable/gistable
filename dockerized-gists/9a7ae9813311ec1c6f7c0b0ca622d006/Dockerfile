FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "pyvirtualdisplay"]
RUN ["pip", "install", "selenium"]
CMD ["python", "snippet.py"]