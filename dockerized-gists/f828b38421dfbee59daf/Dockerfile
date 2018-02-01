FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "moviepy"]
RUN ["pip", "install", "ode"]
RUN ["pip", "install", "vapory"]
CMD ["python", "snippet.py"]