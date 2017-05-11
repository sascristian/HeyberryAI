not working -> https://github.com/MycroftAI/mycroft-core/issues/715

reddit lib praw fails to load

# Mycroft Wallpaper Skill

Downloads wallpapers from reddit, changes wallpaper every X seconds or on command

Supports Kde, gnome, mate and lubuntu desktops (only tested on mate, please give feedback)

## Getting Started

git clone to mycroft skills folder

### Prerequisites

You need a reddit API

requirements
```
praw
```

### Installing

```
pip install praw
```


### Usage

Change wallpaper
```
Changes wallpaper to a random one
```

Downloads wallpaper
```
Downloads new wallpapers
```

Delete wallpaper
```
Deletes wallpapers from folder
```

Cycle Start
```
Starts cycling wallpapers
```

Cycle Stop
```
Stops cycling wallpapers
```


### Configuring

**Chosing Desktop Environment**

in line 26 of __init__.py change self.desktop to "kde", "mate","gnome" or "lubuntu"

**Chosing Subreddit to source wallpapers from**

in line 30 of __init__.py change self.SUBREDDIT to desired subreddit, default = wallpapers can also use for example ImaginaryBestof

**Chosing Max wallpapers number**

in line 36 of __init__.py change self.MAXPOSTS to max number of posts to scan for pictures

**Chosing Time between wallpapers**

in line 37 of __init__.py change self.TIMEBETWEENIMAGES to seconds between wallpaper change

**Activating wallpaper cycling**

in line 42 of __init__.py change self.cycleflag to True or False, still not implemented as intent, only on startup for now

**Populate with new wallpapers on start up**

in line 47 of __init__.py change self.populate to True or False, on skill loading will populate with new wallpapers



## Authors

* **Jarbas AI** - [JarbasAI](https://github.com/JarbasAI)

## License

This project is licensed under the free for all license

## Acknowledgments

* Mycroft-Core - Thankx for making an open-source AI!
* Idea taken from - https://github.com/ssimunic/Daily-Reddit-Wallpaper/blob/master/change_wallpaper_reddit.py

