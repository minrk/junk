FROM alpine:3.6
# take a while and then fail
# the date
ADD date /tmp/date

RUN sleep 60
RUN sleep 60
RUN sleep 60
RUN sleep 60
RUN sleep 60

RUN exit 1
RUN touch /tmp/foo
