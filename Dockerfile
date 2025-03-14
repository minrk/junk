FROM alpine
# take a while and then fail
# the failure prevents this layer from getting into the build cache
RUN dd if=/dev/zero of=/tmp/blob bs=1M count=5000
RUN echo 2025-03-14T22:49 > /tmp/bust
CMD ["exit", "1"]
