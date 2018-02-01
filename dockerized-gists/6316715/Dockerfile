FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "csvkit"]
RUN ["pip", "install", "luigi"]
CMD ["python", "snippet.py"]