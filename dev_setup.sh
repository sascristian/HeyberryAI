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

found_exe() {
    hash "$1" 2>/dev/null
}

install_deps() {
    echo "Installing packages..."
    if found_exe sudo; then
        SUDO=sudo
    fi
    
    if found_exe apt-get; then
        $SUDO apt-get install -y git python python-dev python-setuptools python-virtualenv python-gobject-dev virtualenvwrapper libtool libffi-dev libssl-dev autoconf automake bison swig libglib2.0-dev s3cmd portaudio19-dev mpg123 screen flac curl libicu-dev pkg-config automake libjpeg-dev libfann-dev
    elif found_exe pacman; then
        $SUDO pacman -S --needed git python2 python2-pip python2-setuptools python2-virtualenv python2-gobject python-virtualenvwrapper libtool libffi openssl autoconf bison swig glib2 s3cmd portaudio mpg123 screen flac curl pkg-config icu automake libjpeg-turbo
    elif found_exe dnf; then
        $SUDO dnf install -y git python python-devel python-pip python-setuptools python-virtualenv pygobject2-devel python-virtualenvwrapper libtool libffi-devel openssl-devel autoconf bison swig glib2-devel s3cmd portaudio-devel mpg123 mpg123-plugins-pulseaudio screen curl pkgconfig libicu-devel automake libjpeg-turbo-devel fann-devel
    else
        if found_exe tput; then
			green="$(tput setaf 2)"
			blue="$(tput setaf 4)"
			reset="$(tput sgr0)"
    	fi
    	echo
        echo "${green}Could not find package manager"
        echo "${green}Make sure to manually install:${blue} git python 2 python-setuptools python-virtualenv pygobject virtualenvwrapper libtool libffi openssl autoconf bison swig glib2.0 s3cmd portaudio19 mpg123 flac curl fann"
        echo $reset
    fi
}

install_deps

# Configure to use the standard commit template for
# this repo only.
# git config commit.template .gitmessage

TOP=$(cd $(dirname $0) && pwd -L)

if [ -z "$WORKON_HOME" ]; then
    VIRTUALENV_ROOT=${VIRTUALENV_ROOT:-"${HOME}/.virtualenvs/jarbas"}
else
    VIRTUALENV_ROOT="$WORKON_HOME/jarbas"
fi

# Check whether to build mimic (it takes a really long time!)
build_mimic='y'
if [[ "$1" == '-sm' ]] ; then
  build_mimic='n'
else
  # first, look for a build of mimic in the folder
  has_mimic=""
  if [[ -f ${TOP}/mimic/bin/mimic ]] ; then
      has_mimic=$( ${TOP}/mimic/bin/mimic -lv | grep Voice )
  fi

  # in not, check the system path
  if [ "$has_mimic" = "" ] ; then
    if [ -x "$(command -v mimic)" ]; then
      has_mimic="$( mimic -lv | grep Voice )"
    fi
  fi

  if ! [ "$has_mimic" == "" ] ; then
    echo "Mimic is installed. Press 'y' to rebuild mimic, any other key to skip."
    read -n1 build_mimic
  fi
fi

# create virtualenv, consistent with virtualenv-wrapper conventions
if [ ! -d ${VIRTUALENV_ROOT} ]; then
   mkdir -p $(dirname ${VIRTUALENV_ROOT})
  virtualenv -p python2.7 ${VIRTUALENV_ROOT}
fi

source ${VIRTUALENV_ROOT}/bin/activate
cd ${TOP}
easy_install pip
pip install --upgrade virtualenv

# copy global open-cv to virtual env
# https://medium.com/@manuganji/installation-of-opencv-numpy-scipy-inside-a-virtualenv-bf4d82220313
sudo cp /usr/lib/python2.7/dist-packages/cv* $VIRTUALENV_ROOT/lib/python2.7/site-packages/

# tensorflow from binary
pip install --upgrade https://storage.googleapis.com/tensorflow/linux/cpu/tensorflow-1.2.1-cp27-none-linux_x86_64.whl

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

# nltk
python -m nltk.downloader wordnet
python -m nltk.downloader punkt

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

if [[ "$build_mimic" == 'y' ]] || [[ "$build_mimic" == 'Y' ]]; then
  echo "WARNING: The following can take a long time to run!"
  "${TOP}/scripts/install-mimic.sh" " ${CORES}"
else
  echo "Skipping mimic build."
fi

# install pygtk for desktop_launcher skill
# "${TOP}/scripts/install-pygtk.sh" " ${CORES}"


# get geckodriver to usr/bin for browser service
wget https://github.com/mozilla/geckodriver/releases/download/v0.18.0/geckodriver-v0.18.0-linux64.tar.gz
tar -xvzf geckodriver-v0.18.0-linux64.tar.gz
chmod +x geckodriver
sudo mv geckodriver /usr/local/bin/
sudo rm -rf geckodriver-v0.18.0-linux64.tar.gz