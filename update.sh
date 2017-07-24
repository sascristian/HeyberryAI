./update-dev.sh
./mycroft.sh stop
killall screen
git pull
./mycroft.sh start --client
screen -list