sudo apt-get install llvm

# download tacotron pretrained model
wget http://data.keithito.com/data/speech/tacotron-20170720.tar.bz2

# extract
tar -xjvf tacotron-20170720.tar.bz2

# mov and remove bz2
mv ./tacotron-20170720 ./trained
rm -rf tacotron-20170720.tar.bz2

# install python requirements
sudo pip install -r requirements.txt

# tensorflow from binary
# TODO detect host env and select package
pip install --upgrade https://storage.googleapis.com/tensorflow/linux/cpu/tensorflow-1.2.1-cp27-none-linux_x86_64.whl
