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

# Configure to use the standard commit template for
# this repo only.
#git config commit.template .gitmessage

TOP=$(cd $(dirname $0) && pwd -L)

if [ -z "$WORKON_HOME" ]; then
    VIRTUALENV_ROOT=${VIRTUALENV_ROOT:-"${HOME}/.virtualenvs/jarbas"}
else
    VIRTUALENV_ROOT="$WORKON_HOME/jarbas"
fi

# no mimic

# create virtualenv, consistent with virtualenv-wrapper conventions
if [ ! -d ${VIRTUALENV_ROOT} ]; then
   mkdir -p $(dirname ${VIRTUALENV_ROOT})
  virtualenv -p python2.7 ${VIRTUALENV_ROOT}
fi

source ${VIRTUALENV_ROOT}/bin/activate
cd ${TOP}
easy_install pip
pip install --upgrade virtualenv

# fixed tzwhere
pip install git+https://github.com/seahawk1986/pytzwhere.git@fix_install

# install other requirements
if ! pip install -r requirements.txt; then
    echo "Warning: Failed to install all requirements. Continue? y/N"
    read -n1 continue
    if [[ "$continue" != "y" ]] ; then
        exit 1
    fi
fi

# nltk wordnet

python -m nltk.downloader wordnet

if  [[ $(free|awk '/^Mem:/{print $2}') -lt  1572864 ]] ; then
  CORES=1
else 
  CORES=$(nproc)
fi

echo "Building with $CORES cores."

#build and install pocketsphinx
#cd ${TOP}
#${TOP}/scripts/install-pocketsphinx.sh -q


# install pygtk for desktop_launcher skill
"${TOP}/scripts/install-pygtk.sh"


# get geckodriver to usr/bin for browser service
wget https://github.com/mozilla/geckodriver/releases/download/v0.18.0/geckodriver-v0.18.0-linux64.tar.gz
tar -xvzf geckodriver-v0.18.0-linux64.tar.gz
chmod +x geckodriver
sudo mv geckodriver /usr/local/bin/