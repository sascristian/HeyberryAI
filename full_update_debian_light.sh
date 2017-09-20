./mycroft.sh stop
# WARNING overwrite all local changes
git fetch origin patch-15
git reset --hard FETCH_HEAD
# Clean all files not in repo, will erase keys and all data in this folder
# git clean -df
./install_light.sh
./update-dev-light.sh
screen -list