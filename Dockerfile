FROM jupyter/base-notebook
USER root
RUN apt-get update && apt-get install -y ssh iputils-ping dnsutils curl wget nano
USER 1000
