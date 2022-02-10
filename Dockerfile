FROM python:3.9
COPY job.py job.py
RUN python job.py
