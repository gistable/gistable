FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "pyaudio"]
RUN ["pip", "install", "pyqtgraph"]
RUN ["pip", "install", "numpy"]
RUN ["pip", "install", "PyQt4"]
CMD ["python", "snippet.py"]