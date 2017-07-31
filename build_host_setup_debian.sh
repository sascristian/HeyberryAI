#!/usr/bin/env bash

sudo apt-get install -y \
    git \
    python \
    python-dev \
    python-setuptools \
    python-virtualenv \
    python-gobject-dev \
    virtualenvwrapper \
    libtool \
    libffi-dev \
    libssl-dev \
    autoconf \
    automake \
    bison \
    swig \
    libglib2.0-dev \
    s3cmd \
    portaudio19-dev \
    mpg123 \
    screen \
    flac \
    curl \
    libicu-dev \
    pkg-config \
    automake \
    libjpeg-dev
    xvfb \
    firefox \
    vlc \
    libopencv-dev \
    python-opencv \
    libxml2-dev \
    libxslt1-dev \
    build-essential \
    gfortran \
    libatlas-base-dev \
    gnupg \
    libcurl4-openssl-dev

# get geckodriver to usr/bin for browser service
wget https://github.com/mozilla/geckodriver/releases/download/v0.18.0/geckodriver-v0.18.0-linux64.tar.gz
tar -xvzf geckodriver-v0.18.0-linux64.tar.gz
chmod +x geckodriver
sudo mv geckodriver /usr/local/bin/