FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "pbkdf2"]
RUN ["pip", "install", "requests"]
RUN ["pip", "install", "beaker"]
RUN ["pip", "install", "bottle"]
CMD ["python", "snippet.py"]