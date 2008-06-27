import face_recognition
import os
from mycroft.skills.core import MycroftSkill
from jarbas_utils.skill_dev_tools import ResponderBackend
from jarbas_utils.skill_tools import FaceRecognitionQuery

__author__ = 'jarbas'


class FaceRecognitionSkill(MycroftSkill):

    def __init__(self):
        super(FaceRecognitionSkill, self).__init__()
        self.reload_skill = False
        self.known_faces = {}
        # load known faces
        faces = os.listdir(os.path.dirname(__file__) + "/known faces")
        # Load the jpg files into numpy arrays
        for face in faces:
            # Get the face encodings for each face in each image file
            # Since there could be more than one face in each image, it returns a list of encordings.
            # But since i assume each image only has one face, I only care about the first encoding in each image, so I grab index 0.
            self.log.info("loading face encodings for " + face)
            self.known_faces[face] = face_recognition.face_encodings(face_recognition.load_image_file(os.path.dirname(__file__) + "/known faces/" + face))[0]

    def initialize(self):
        self.responder = ResponderBackend(self.name, self.emitter, self.log)
        self.responder.set_response_handler("face.recognition.request", self.handle_face_recognition_request)
        # TODO test face recog intent

    def handle_face_recognition_request(self, message):
        if message.context is not None:
            self.message_context.update(message.context)
        face = message.data.get("file", message.data.get("PicturePath"))
        if face is None:
            self.log.error("no file!")
            face = "missing file"
        else:
            self.set_context("PicturePath", face)
        result = "unknown person"
        # read unknown image
        self.log.info("loading unknown image")
        try:
            unknown_image = face_recognition.load_image_file(face)
        except:
            self.log.error("loading file failed")
        self.log.info("getting face encodings of unknown image")
        try:
            encoding = face_recognition.face_encodings(unknown_image)[0]
            for person in self.known_faces.keys():
                self.log.info("comparing to person " + person)
                # check if unknown person is this face, by comparing face encodings
                match = face_recognition.compare_faces([self.known_faces[person]], encoding)
                # match is an array of True/False telling if the unknown face matched anyone in the known_faces array
                if match[0]:
                    result = person[:person.find(".", -1)]
                    self.log.info("match found, unknown image is " + result)
                    break
        except:
            self.log.error("no face detected in provided image")

        self.message_context = self.get_message_context(message.context)
        data = {"result": result}
        self.responder.update_response_data(data, self.message_context)

    def handle_test_face_recognition_intent(self, message):
        picture_path = message.data.get("file", message.data.get("PicturePath"))
        if not picture_path:
            picture_path = os.path.dirname(__file__) + "/test.jpg"
        recognizer = FaceRecognitionQuery(self.name, self.emitter, 60)
        result = recognizer.face_recognition_from_file(picture_path,
                                                      context=self.message_context)

    def stop(self):
        pass


def create_skill():
    return FaceRecognitionSkill()
