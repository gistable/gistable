FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "joblib"]
RUN ["pip", "install", "numpy"]
RUN ["pip", "install", "s3io"]
CMD ["python", "snippet.py"]