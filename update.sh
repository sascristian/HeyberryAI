export PATH=$PATH:/home/test/mycroft-server/server_skills/browser_service
killall screen
git pull
./mycroft.sh start
screen -list