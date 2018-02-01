FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "dronekit"]
RUN ["pip", "install", "pymavlink"]
CMD ["python", "snippet.py"]