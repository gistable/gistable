FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "mido"]
RUN ["pip", "install", "numpy"]
RUN ["pip", "install", "vapory"]
RUN ["pip", "install", "moviepy"]
CMD ["python", "snippet.py"]