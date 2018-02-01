FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "readbot"]
RUN ["pip", "install", "pyperclip"]
CMD ["python", "snippet.py"]