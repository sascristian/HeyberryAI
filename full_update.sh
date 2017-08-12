./mycroft.sh stop
git pull
python -m nltk.downloader wordnet
./build_host_setup_debian.sh
./update-dev.sh
./mycroft.sh start
screen -list