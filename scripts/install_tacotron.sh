if [ -z "$WORKON_HOME" ]; then
    VIRTUALENV_ROOT=${VIRTUALENV_ROOT:-"${HOME}/.virtualenvs/jarbas"}
else
    VIRTUALENV_ROOT="$WORKON_HOME/jarbas"
fi

source "${VIRTUALENV_ROOT}/bin/activate"


sudo apt-get install llvm

# download tacotron pretrained model
wget http://data.keithito.com/data/speech/tacotron-20170720.tar.bz2

# extract
tar -xjvf tacotron-20170720.tar.bz2

# mov and remove bz2
mv ./tacotron-20170720 ../jarbas_models/tf_tacotron/trained
rm -rf tacotron-20170720.tar.bz2

# install python requirements
pip install -r tacotron_requirements.txt

# tensorflow from binary
./install_tensorflow.sh