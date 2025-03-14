FROM alpine:3.6
# take a while and then fail
# the failure prevents this layer from getting into the build cache
RUN dd if=/dev/zero of=/tmp/blob bs=1M count=1000
CMD ["exit", "1"]
