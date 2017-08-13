./mycroft.sh stop
git pull
./build_host_setup_debian.sh
./update-dev.sh
python -m nltk.downloader wordnet
./mycroft.sh start
screen -list