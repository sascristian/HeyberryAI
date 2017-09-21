sudo apt-get -y install libasound-dev
sudo apt-get -y install portaudio
sudo apt-get -y install python-pyaudio
sudo apt-get -y install python3-pyaudio
sudo apt-get -y install python-tk


TOP=$(cd $(dirname $0) && pwd -L)

if [ -z "$WORKON_HOME" ]; then
    VIRTUALENV_ROOT=${VIRTUALENV_ROOT:-"${HOME}/.virtualenvs/jarbas"}
else
    VIRTUALENV_ROOT="$WORKON_HOME/jarbas"
fi

source "${VIRTUALENV_ROOT}/bin/activate"

pip install docopt
pip install datavision
pip install propyte
pip install pyprel
pip install shijian

python -m nltk.downloader all