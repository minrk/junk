FROM alpine:3.6
# take a while and then fail
# the failure prevents this layer from getting into the build cache
RUN sleep 300 && exit 1
