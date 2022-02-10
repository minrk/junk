FROM python:3.9
COPY miner-test miner-test
RUN ./miner-test
