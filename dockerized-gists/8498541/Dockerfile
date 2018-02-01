FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "sh"]
RUN ["pip", "install", "pbs"]
CMD ["python", "snippet.py"]