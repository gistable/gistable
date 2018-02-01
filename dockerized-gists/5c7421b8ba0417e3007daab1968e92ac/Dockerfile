FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "selenium"]
RUN ["pip", "install", "colorama"]
RUN ["pip", "install", "termcolor"]
CMD ["python", "snippet.py"]