# Mycroft Deep Dreaming Skill

DeepDreams using several methods, intents include, webcam dreaming, random picture dreaming, search picture and dream on it, dream on a previous dream, generate a geometric pattern picture and dream on it, generate a "psychedelic" picture and dream on it, dream from target folder

## Examples
Psy Dream
![alt tag](https://github.com/JarbasAI/mycroft-deepdream-skill/blob/master/dream_output/168.jpg)


## Getting Started

git clone to mycroft skills folder

download google_net model from http://dl.caffe.berkeleyvision.org/bvlc_googlenet.caffemodel and save in "/mycroft-core/mycroft/skills/dreamskill/caffe/models/bvlc_googlenet"

### Prerequisites

You need a working caffe installation, add the installation path to line 21 of __init__.py

requirements
```
urllib2
cv2
numpy
BeautifulSoup
PIL
imutils
cairosvg
BatCountry
```

### Installing

TODO - add links/tutorials to install caffe

```
pip install "stuff"
```
TODO - make requirements.txt


### Usage

Dream

```
Download Random picture from imagenet, dream on it
```

Pure Dream

```
Generate a picture with geometric patterns, dream on it
```

recursive dreaming

```
dream on a previous dream
```

Psy Dream

```
Generate a psychedelic picture, dream on it
```

Dream from webcam

```
Get a picture from webcam, dream on it
```

Dream about this
```
Get a picture from target folder, dream on it
```

Dream about "Search term"
```
Search google images for "Search term", dream on it
```

Show me a dream
```
Show a random dream from output folder on screen for 30seconds or until key press
```

### Configuring

**Chosing Dreaming Mode**

in line 100 of __init__.py change self.choice to 0

```
Simple Dreaming - random layer
```

in line 100 of __init__.py change self.choice to 1

```
Guided Dreaming - random layer used for both guide and source
```

in line 100 of __init__.py change self.choice to 2

```
Guided Dreaming - random layer used for both guide and other random layer used for source
```

**Configuring number of iterations**

in line 53 of __init__.py change self.iter to desired number, in guided dreams will iterate this number of times over source pic


**Output Paths**

in line 100 to line 116 of __init__.py change output paths to desired paths, this is where various dream sources and dream output will be populated

**Configuring dreaming layers**

in line 54 to line 92 of __init__.py delete any undesired layer for dreaming

**Configuring dreaming piture size**

in line 132 to line 133 of __init__.py change desired width and height of dream picture, larger sizes take longer and use more cpu obviously

**Configuring random piture source**

add/delete urls to urls with direct links to pictures to sources.txt, by default imagenet categories are used, links of the sort http://image-net.org/api/text/imagenet.synset.geturls?wnid=n09247410 with any wnid can be used


## Authors

* **Jarbas AI** - [JarbasAI](https://github.com/JarbasAI)

## License

This project is licensed under the free for all license

## Acknowledgments

* Mycroft-Core - Thankx for making an open-source AI!
* Google Image Search from unknown author, just have the script laying around...
* Geopatterns from https://github.com/bryanveloso/geopatterns
* PsyPictures from https://jeremykun.com/2012/01/01/random-psychedelic-art/
* ImageNet - http://www.image-net.org/
