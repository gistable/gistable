FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "jinja2"]
RUN ["pip", "install", "twitter"]
RUN ["pip", "install", "pyquery"]
CMD ["python", "snippet.py"]