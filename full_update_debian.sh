./mycroft.sh stop
git pull
./build_host_setup_debian.sh
./update-dev.sh
./mycroft.sh start
screen -list