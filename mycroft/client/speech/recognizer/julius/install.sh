sudo apt install libasound2-dev
wget https://github.com/julius-speech/julius/archive/master.zip
mv master.zip julius-master.zip
unzip julius-master.zip
rm -rf julius-master.zip
cd julius-master
sudo ./configure --with-mictype=alsa
sudo make
sudo make install
mkdfa.pl julius