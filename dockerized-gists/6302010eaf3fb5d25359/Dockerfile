FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "myfitnesspal"]
RUN ["pip", "install", "requests"]
RUN ["pip", "install", "keyring"]
CMD ["python", "snippet.py"]