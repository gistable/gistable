FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "boto"]
RUN ["pip", "install", "nagiosplugin"]
CMD ["python", "snippet.py"]