ARG PYTHON_VERSION=3.7

FROM python:$PYTHON_VERSION
ENV PYTHONUNBUFFERED 1

ARG BUILD_ENV=dev

ENV BUILD_ENV="$BUILD_ENV"
ENV PYTHON_VERSION="$PYTHON_VERSION"

LABEL payroll.distro.name=linux
LABEL payroll.distro.release=debian
LABEL payroll.image.name=payroll-web
LABEL payroll.build.env="$BUILD_ENV"
LABEL payroll.python.version="$PYTHON_VERSION"

# update package lists, fix broken system packages and install locales
RUN apt-get update && \
    apt-get -f install && \
    apt-get install -y locales locales-all memcached

# setting locales
ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

# Copy requirements.txt file
COPY ./requirements.txt /requirements.txt

# Update pip version and build wheel archive
RUN pip install --upgrade pip wheel
RUN pip wheel --wheel-dir=/wheelhouse -r requirements.txt

# Install pip packages from wheel archives
RUN pip install --no-index -f /wheelhouse -r requirements.txt

# OUTPUT: Build artefacts (Wheels)
VOLUME /wheelhouse

# load project files and set work directory
ADD . /app
WORKDIR /app

# create user and add to docker group
RUN adduser --disabled-password --gecos '' payroll && \
    groupadd docker && \
    usermod -aG docker payroll

# grant newly created user permissions on essential files
RUN chown -R payroll:$(id -gn payroll) /app/ && \
    chmod +x scripts/start_server.sh && \
    chmod +x scripts/wait_for_db.sh

# change user to newly created user
USER payroll
