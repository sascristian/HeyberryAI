./mycroft.sh stop
# WARNING overwrite all local changes
git fetch origin patch-15
git reset --hard FETCH_HEAD
git clean -df
./build_host_setup_debian.sh
./update-dev.sh
./mycroft.sh start
screen -list