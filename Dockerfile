FROM alpine
# take a while and then fail
# the failure prevents this layer from getting into the build cache
RUN echo 2025-03-14T22:49 > /tmp/bust
RUN dd if=/dev/zero of=/tmp/blob bs=1M count=5000
CMD ["exit", "1"]
