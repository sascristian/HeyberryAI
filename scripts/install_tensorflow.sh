if [ -z "$WORKON_HOME" ]; then
    VIRTUALENV_ROOT=${VIRTUALENV_ROOT:-"${HOME}/.virtualenvs/jarbas"}
else
    VIRTUALENV_ROOT="$WORKON_HOME/jarbas"
fi

source "${VIRTUALENV_ROOT}/bin/activate"

# tensorflow from binary
# TODO detect host env and select package

if found_exe apt-get; then
    pip install --upgrade https://storage.googleapis.com/tensorflow/linux/cpu/protobuf-3.1.0-cp27-none-linux_x86_64.whl
    pip install --upgrade https://storage.googleapis.com/tensorflow/linux/cpu/tensorflow-1.3.0-cp27-none-linux_x86_64.whl
else
    echo
    echo "${green}Could not install tensorflow"
    echo $reset
fi