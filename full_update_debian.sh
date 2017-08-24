./mycroft.sh stop
# WARNING overwrite all local changes
git fetch origin patch-15
git reset --hard FETCH_HEAD
# Clean all files not in repo, will erase keys and all data in this folder
# git clean -df
./build_host_setup_debian.sh
./update-dev.sh
screen -list