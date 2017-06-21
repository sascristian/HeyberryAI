export PATH=$PATH:/home/test/mycroft-server/server_skills/browser_service
./mycroft.sh stop
git pull
./mycroft.sh start
screen -list