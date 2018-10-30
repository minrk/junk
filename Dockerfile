FROM python:3.6-alpine
# take a while and then fail
# the failure prevents this layer from getting into the build cache
ARG BURN_TIME
ARG BURN_CPUS
ADD cpuburn.py /tmp/cpuburn.py
RUN python /tmp/cpuburn.py && exit 1
