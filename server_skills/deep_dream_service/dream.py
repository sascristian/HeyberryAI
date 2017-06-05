# import the necessary packages
from batcountry import BatCountry
from PIL import Image
import numpy as np
from os.path import dirname
import sys

path = "home/test/caffe"  # self.config["caffe_path"]
sys.path.insert(0, path + '/python')

# we can't stop here...
bc = BatCountry(path + "/models/bvlc_googlenet")
image = bc.dream(np.float32(Image.open(dirname(__file__)+"/screenshot_1.jpg")), end="conv2/3x3")
bc.cleanup()

# write the output image to file
result = Image.fromarray(np.uint8(image))
result.save(dirname(__file__)+"output.jpg")