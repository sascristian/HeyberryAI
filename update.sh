./mycroft.sh stop
killall screen
git pull
./mycroft.sh start -c
screen -list