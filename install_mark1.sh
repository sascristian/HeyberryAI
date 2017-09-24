#!/usr/bin/env bash
######################################################
# dev_setup.sh
# @author sean.fitzgerald (aka clusterfudge)
#
# The purpose of this script is to create a self-
# contained development environment using
# virtualenv for python dependency sandboxing.
# This script will create a virtualenv (using the
# conventions set by virtualenv-wrapper for
# location and naming) and install the requirements
# laid out in requirements.txt, pocketsphinx, and
# pygtk into the virtualenv. Mimic will be
# installed and built from source inside the local
# checkout.
#
# The goal of this script is to create a development
# environment in user space that is fully functional.
# It is expected (and even encouraged) for a developer
# to work on multiple projects concurrently, and a
# good OSS citizen respects that and does not pollute
# a developers workspace with it's own dependencies
# (as much as possible).
# </endRant>
######################################################

# exit on any error
set -Ee

if [ $(id -u) -eq 0 ]; then
  echo "This script should not be run as root or with sudo."
  exit 1
fi

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
    libjpeg-dev \
    python-opencv \
    libfann-dev \
    libgmp-dev \
    gnupg


TOP=$(cd $(dirname $0) && pwd -L)

if [ -z "$WORKON_HOME" ]; then
    VIRTUALENV_ROOT=${VIRTUALENV_ROOT:-"${HOME}/.virtualenvs/jarbas"}
else
    VIRTUALENV_ROOT="$WORKON_HOME/jarbas"
fi


cd "${TOP}"
easy_install pip


# install requirements (except pocketsphinx)
# removing the pip2 explicit usage here for consistency with the above use.

if ! pip install -r requirements_light.txt; then
    echo "Warning: Failed to install all requirements. Continue? y/N"
    read -n1 continue
    if [[ "$continue" != "y" ]] ; then
        exit 1
    fi
fi

SYSMEM=$(free|awk '/^Mem:/{print $2}')
MAXCORES=$(($SYSMEM / 512000))
CORES=$(nproc)

if [[ ${MAXCORES} -lt ${CORES} ]]; then
  CORES=${MAXCORES}
fi
echo "Building with $CORES cores."

#build and install pocketsphinx
#cd ${TOP}
#${TOP}/scripts/install-pocketsphinx.sh -q
#build and install mimic
cd "${TOP}"

# install pygtk for desktop_launcher skill
# "${TOP}/scripts/install-pygtk.sh" " ${CORES}"

# md5sum requirements.txt dev_setup.sh > .installed

# PicoTTS
"${TOP}/scripts/install-pico.sh"