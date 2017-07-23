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
    xvfb \
    firefox \
    vlc \
    libopencv-dev \
    python-opencv \
    libxml2-dev \
    libxslt1-dev \
    build-essential \
    gfortran \
    libatlas-base-dev

# copy geckodriver to usr/bin for browser service
TOP=$(cd $(dirname $0) && pwd -L)
sudo cp ${TOP}/geckodriver /usr/bin