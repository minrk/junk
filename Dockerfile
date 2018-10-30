FROM python:3.6-alpine
# take a while and then fail
# the failure prevents this layer from getting into the build cache
ADD cpuburn.py /tmp/cpuburn.py
RUN python /tmp/cpuburn.py
RUN exit 1 # never succeed
