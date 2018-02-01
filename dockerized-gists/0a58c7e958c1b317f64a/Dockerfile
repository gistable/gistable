FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "numpy"]
RUN ["pip", "install", "ui"]
RUN ["pip", "install", "console"]
CMD ["python", "snippet.py"]