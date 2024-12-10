FROM ubuntu:latest
LABEL authors="Stend"

ENTRYPOINT ["top", "-b"]