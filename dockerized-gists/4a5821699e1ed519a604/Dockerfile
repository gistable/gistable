FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "unidecode"]
RUN ["pip", "install", "fuzzywuzzy"]
RUN ["pip", "install", "unicodecsv"]
CMD ["python", "snippet.py"]