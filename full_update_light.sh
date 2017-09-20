./mycroft.sh stop
# WARNING overwrite all local changes
git fetch origin patch-15
git reset --hard FETCH_HEAD
# Clean all files not in repo, will erase keys and all data in this folder
# git clean -df


found_exe() {
    hash "$1" 2>/dev/null
}

install_deps() {
    echo "Installing packages..."
    if found_exe sudo; then
        SUDO=sudo
    fi

    if found_exe apt-get; then
        $SUDO apt-get install -y \
            git \
            python \
            python-dev \
            python-setuptools \
            python-virtualenv \
            python-gobject-dev \
            virtualenvwrapper \
            libtool \
            libffi-dev \
            libssl-dev \
            autoconf \
            automake \
            bison \
            swig \
            libglib2.0-dev \
            s3cmd \
            portaudio19-dev \
            mpg123 \
            screen \
            flac \
            curl \
            libicu-dev \
            pkg-config \
            automake \
            libjpeg-dev \
            python-opencv \
            libfann-dev \
            libgmp-dev \
            gnupg



    elif found_exe pacman; then
        echo "${green}Jarbas untested for pacman, expect trouble"
        $SUDO pacman -S --needed git python2 python2-pip python2-setuptools python2-virtualenv python2-gobject python-virtualenvwrapper libtool libffi openssl autoconf bison swig glib2 s3cmd portaudio mpg123 screen flac curl pkg-config icu automake libjpeg-turbo

    elif found_exe dnf; then
        echo "${green}Jarbas untested for dnf, expect trouble"
        $SUDO dnf install -y git python python-devel python-pip python-setuptools python-virtualenv pygobject2-devel python-virtualenvwrapper libtool libffi-devel openssl-devel autoconf bison swig glib2-devel s3cmd portaudio-devel mpg123 mpg123-plugins-pulseaudio screen curl pkgconfig libicu-devel automake libjpeg-turbo-devel fann-devel

    else
        if found_exe tput; then
			green="$(tput setaf 2)"
			blue="$(tput setaf 4)"
			reset="$(tput sgr0)"
    	fi
    	echo
        echo "${green}Could not find package manager"
        echo "${green}Make sure to manually install:${blue} git python 2 python-setuptools python-virtualenv pygobject virtualenvwrapper libtool libffi openssl autoconf bison swig glib2.0 s3cmd portaudio19 mpg123 flac curl fann"
        echo $reset
    fi
}

install_deps


./update-dev-light.sh
screen -list