FROM alpine
RUN dd if=/dev/random of=/blob bs=3G count=1
