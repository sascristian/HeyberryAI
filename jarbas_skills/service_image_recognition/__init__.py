# Copyright 2015 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""Simple image classification with Inception.
Run image classification with Inception trained on ImageNet 2012 Challenge data
set.
This program creates a graph from a saved GraphDef protocol buffer,
and runs inference on an input JPEG image. It outputs human readable
strings of the top 5 predictions along with their probabilities.
Change the --image_file argument to any jpg image to compute a
classification of that image.
Please see the tutorial and website for a detailed description of how
to use this script to perform image recognition.
https://tensorflow.org/tutorials/image_recognition/
"""

from __future__ import absolute_import
from __future__ import division

import os.path
import re
from six.moves import urllib
import tensorflow as tf
from mycroft import MYCROFT_ROOT_PATH as root_path
import numpy as np
import os, urllib, tarfile
from os.path import dirname
from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from jarbas_utils.skill_tools import ImageRecognitionQuery
from jarbas_utils.skill_dev_tools import ResponderBackend

__author__ = 'jarbas'


class ImageRecognitionSkill(MycroftSkill):

    def __init__(self):
        super(ImageRecognitionSkill, self).__init__(name="ImageRecognitionSkill")
        self.reload_skill = False
        # Path to classify_image_graph_def.pb,
        # imagenet_synset_to_human_label_map.txt, and
        # imagenet_2012_challenge_label_map_proto.pbtxt
        self.model_dir = root_path + "/jarbas_models/tf_inception"
        # where to download
        self.DATA_URL = 'http://download.tensorflow.org/models/image/imagenet/inception-2015-12-05.tgz'
        # number of predictions to return
        self.num_top_predictions = 5
        # download model if missing
        #self.maybe_download_and_extract()
        # Creates node ID --> English string lookup.
        self.node_lookup = NodeLookup(self.model_dir)

    def initialize(self):
        self.responder = ResponderBackend(self.name, self.emitter, self.log)
        self.responder.set_response_handler("image.classification.request",
                                            self.handle_image_classification_request)

        # TODO improve keywords
        image_recog_status_intent = IntentBuilder(
            "ImageClassficationStatusIntent") \
            .require("imgstatus").build()
        self.register_intent(image_recog_status_intent,
                             self.handle_image_classification_intent)

    def maybe_download_and_extract(self):
        # TODO move this into install, not run time
        # """Download and extract model tar file."""
        dest_directory = self.model_dir
        if not os.path.exists(dest_directory):
            os.makedirs(dest_directory)
        filename = self.DATA_URL.split('/')[-1]
        filepath = os.path.join(dest_directory, filename)
        if not os.path.exists(filepath):
            self.log.info("Downloading model to " + filepath)
            urllib.urlretrieve(self.DATA_URL, filepath)
            self.log.info('Successfully downloaded' + filename)
        # TODO check if extracted befoe extracting
        tarfile.open(filepath, 'r:gz').extractall(dest_directory)

    def run_inference_on_image(self, image):
        # """Runs inference on an image.
        if not tf.gfile.Exists(image):
            tf.logging.fatal('File does not exist %s', image)
        image_data = tf.gfile.FastGFile(image, 'rb').read()

        # Creates graph from saved graph_def.pb.
        with tf.gfile.FastGFile(os.path.join(
                self.model_dir, 'classify_image_graph_def.pb'), 'rb') as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())
            _ = tf.import_graph_def(graph_def, name='')

        with tf.Session() as sess:
            # Some useful tensors:
            # 'softmax:0': A tensor containing the normalized prediction across
            #   1000 labels.
            # 'pool_3:0': A tensor containing the next-to-last layer containing 2048
            #   float description of the image.
            # 'DecodeJpeg/contents:0': A tensor containing a string providing JPEG
            #   encoding of the image.
            # Runs the softmax tensor by feeding the image_data as input to the graph.
            softmax_tensor = sess.graph.get_tensor_by_name('softmax:0')
            predictions = sess.run(softmax_tensor,
                                   {'DecodeJpeg/contents:0': image_data})
            predictions = np.squeeze(predictions)

            top_k = predictions.argsort()[-self.num_top_predictions:][::-1]
            results = []
            for node_id in top_k:
                human_string = self.node_lookup.id_to_string(node_id)
                score = predictions[node_id]
                self.log.info('%s (score = %.5f)' % (human_string, score))
                score = score * 100
                score = str(score)[:4]
                results.append([human_string, score])
            return results

    def handle_image_classification_intent(self, message):
        self.speak_dialog("imgrecogstatus")
        imgrecog = ImageRecognitionQuery(self.name, self.emitter, timeout=130)
        path = message.data.get("PicturePath", dirname(__file__)+"/obama.jpg")
        results = imgrecog.get_classification(path)
        if not results:
            self.log.error("no classification received")
            return
        self.log.info(results)
        label, score = results[0]
        self.speak("test image classification is " + label + " with a score of " + score + " per cent")

    def handle_image_classification_request(self, message):
        if message.context is not None:
            self.message_context.update(message.context)
        pic = message.data.get("file", message.data.get("PicturePath"))
        if pic is None:
            self.log.error("Could not read file to classify")
            self.speak("Could not read file to classify")
            return
        self.set_context("PicturePath", pic)
        self.log.info("predicting")
        result = self.run_inference_on_image(pic)
        self.log.info("prediction ready, sending data")
        self.log.debug(result)
        # send result
        msg_data = {"classification": result}
        self.responder.update_response_data(msg_data, self.message_context)

    def stop(self):
        pass


def create_skill():
    return ImageRecognitionSkill()


class NodeLookup(object):
  """Converts integer node ID's to human readable labels."""

  def __init__(self,
               model_dir,
               label_lookup_path=None,
               uid_lookup_path=None):
    if not label_lookup_path:
      label_lookup_path = os.path.join(
          model_dir, 'imagenet_2012_challenge_label_map_proto.pbtxt')
    if not uid_lookup_path:
      uid_lookup_path = os.path.join(
          model_dir, 'imagenet_synset_to_human_label_map.txt')
    self.node_lookup = self.load(label_lookup_path, uid_lookup_path)

  def load(self, label_lookup_path, uid_lookup_path):
    """Loads a human readable English name for each softmax node.
    Args:
      label_lookup_path: string UID to integer node ID.
      uid_lookup_path: string UID to human-readable string.
    Returns:
      dict from integer node ID to human-readable string.
    """
    if not tf.gfile.Exists(uid_lookup_path):
      tf.logging.fatal('File does not exist %s', uid_lookup_path)
    if not tf.gfile.Exists(label_lookup_path):
      tf.logging.fatal('File does not exist %s', label_lookup_path)

    # Loads mapping from string UID to human-readable string
    proto_as_ascii_lines = tf.gfile.GFile(uid_lookup_path).readlines()
    uid_to_human = {}
    p = re.compile(r'[n\d]*[ \S,]*')
    for line in proto_as_ascii_lines:
      parsed_items = p.findall(line)
      uid = parsed_items[0]
      human_string = parsed_items[2]
      uid_to_human[uid] = human_string

    # Loads mapping from string UID to integer node ID.
    node_id_to_uid = {}
    proto_as_ascii = tf.gfile.GFile(label_lookup_path).readlines()
    for line in proto_as_ascii:
      if line.startswith('  target_class:'):
        target_class = int(line.split(': ')[1])
      if line.startswith('  target_class_string:'):
        target_class_string = line.split(': ')[1]
        node_id_to_uid[target_class] = target_class_string[1:-2]

    # Loads the final mapping of integer node ID to human-readable string
    node_id_to_name = {}
    for key, val in node_id_to_uid.items():
      if val not in uid_to_human:
        tf.logging.fatal('Failed to locate: %s', val)
      name = uid_to_human[val]
      node_id_to_name[key] = name

    return node_id_to_name

  def id_to_string(self, node_id):
    if node_id not in self.node_lookup:
      return ''
    return self.node_lookup[node_id]