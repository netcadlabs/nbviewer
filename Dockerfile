# Define a builder image
FROM python:3.7-buster as builder

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
RUN apt-get update \
 && apt-get install -yq --no-install-recommends \
    ca-certificates \
    libcurl4-gnutls-dev \
    git

RUN curl -sL https://deb.nodesource.com/setup_12.x | bash
RUN apt install nodejs
RUN node --version && npm --version

# Python requirements
COPY ./requirements-dev.txt /srv/nbviewer/
COPY ./requirements.txt /srv/nbviewer/
RUN python3 -mpip install -r /srv/nbviewer/requirements-dev.txt -r /srv/nbviewer/requirements.txt

WORKDIR /srv/nbviewer

# Copy source tree in
COPY . /srv/nbviewer
RUN python3 setup.py build && \
    python3 -mpip wheel -vv . -w /wheels

# Now define the runtime image
FROM python:3.7-slim-buster
LABEL maintainer="Netcad Innovation Labs <netcadinnovationlabs@gmail.com>"

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update \
 && apt-get install -yq --no-install-recommends \
    ca-certificates \
    libcurl4 \
    git \
    cron \
 && apt-get clean && rm -rf /var/lib/apt/lists/*


COPY --from=builder /wheels /wheels
RUN python3 -mpip install --no-cache /wheels/*

ENV NB_DATA_FOLDER /srv/nbviewer/data
ENV CRON_USERNAME appuser
ENV MPLCONFIGDIR /srv/nbviewer/data

# To change the number of threads use
# docker run -d -e NBVIEWER_THREADS=4 -p 80:8080 nbviewer
ENV NBVIEWER_THREADS 2
WORKDIR /srv/nbviewer
#USER nobody

# Switches to a non-root user and changes the ownership of the /app folder"
RUN useradd appuser && chown -R appuser /srv/nbviewer
USER appuser

EXPOSE 5000
CMD ["python", "-m", "nbviewer", "--port=5000"]
