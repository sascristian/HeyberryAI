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

TOP=$(cd $(dirname $0) && pwd -L)

#if [ -z "$WORKON_HOME" ]; then
#    VIRTUALENV_ROOT=${VIRTUALENV_ROOT:-"${HOME}/.virtualenvs/mycroft"}
#else
#    VIRTUALENV_ROOT="$WORKON_HOME/mycroft"
#fi

# create virtualenv, consistent with virtualenv-wrapper conventions
#if [ ! -d ${VIRTUALENV_ROOT} ]; then
#   mkdir -p $(dirname ${VIRTUALENV_ROOT})
#  virtualenv -p python2.7 ${VIRTUALENV_ROOT}
#fi
#source ${VIRTUALENV_ROOT}/bin/activate

cd ${TOP}
#easy_install pip==7.1.2 # force version of pip
#pip install --upgrade virtualenv

# install requirements (except pocketsphinx)
pip2 install -r requirements.txt 

#CORES=$(nproc)
#echo Building with $CORES cores.

#build and install pocketsphinx
#cd ${TOP}
#${TOP}/scripts/install-pocketsphinx.sh -q

# not on server
#build and install mimic
#cd ${TOP}
#${TOP}/scripts/install-mimic.sh

# install pygtk for desktop_launcher skill
#${TOP}/scripts/install-pygtk.sh

# download and extract tensorflow models
# inception
wget https://storage.googleapis.com/download.tensorflow.org/models/inception5h.zip -P ${TOP}/mycroft/models/inception
wget http://download.tensorflow.org/models/image/imagenet/inception-2015-12-05.tgz -P ${TOP}/mycroft/models/inception
unzip ${TOP}/mycroft/models/inception/inception5h.zip -d ${TOP}/mycroft/models/inception
tar -xzvf ${TOP}/mycroft/models/inception/inception-2015-12-05.tgz ${TOP}/mycroft/models/inception
# vgg19
wget http://www.vlfeat.org/matconvnet/models/beta16/imagenet-vgg-verydeep-19.mat P ${TOP}/mycroft/models/vgg19