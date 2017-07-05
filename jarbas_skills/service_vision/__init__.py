from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.messagebus.message import Message
from mycroft.util.log import getLogger

# try to load display service
import sys
from os.path import dirname, exists
from os import makedirs
sys.path.append(dirname(dirname(__file__)))

#from service_display.displayservice import DisplayService
import time
import numpy as np
import cv2
from imutils.video import FPS
from imutils.video import WebcamVideoStream as eye
import imutils
from time import asctime
__author__ = "jarbas"


class VisionSkill(MycroftSkill):

    def __init__(self):
        super(VisionSkill, self).__init__(name="VisionSkill")
        self.reload_skill = False
        self.external_shutdown = False
        self.external_reload = False
        self.filter = "None"
        # TODO read from config
        self.webcam_path = dirname(__file__) + "/webcam"
        if not exists(self.webcam_path):
            makedirs(self.webcam_path)

    def initialize(self):
       # self.display_service = DisplayService(self.emitter)
        self.init_vision()
        self.emitter.on("vision_request", self.handle_vision_request)
        self.build_intents()

    def build_intents(self):

        describe_what_do_you_see_intent = IntentBuilder("DescribeCurrentVisionIntent"). \
            require("DescribeVisionKeyword").build()

        self.register_intent(describe_what_do_you_see_intent, self.handle_describe_what_do_you_see_intent)

        what_do_you_see_intent = IntentBuilder("CurrentVisionIntent").\
                require("VisionKeyword").build()

        self.register_intent(what_do_you_see_intent, self.handle_what_do_you_see_intent)

        vision_data_intent = IntentBuilder("VisionDataIntent"). \
            require("VisionDataKeyword").build()

        self.register_intent(vision_data_intent, self.handle_vision_data_intent)

        reset_intent = IntentBuilder("ResetVisionIntent"). \
            require("ResetVisionKeyword").build()

        self.register_intent(reset_intent, self.handle_reset_vision_intent)

        smooth_intent = IntentBuilder("SmoothFilterIntent"). \
            require("SmoothKeyword").build()

        self.register_intent(smooth_intent, self.handle_smooth_filter_intent)

        skeleton_intent = IntentBuilder("SkeletonFilterIntent"). \
            require("SkeletonKeyword").build()

        self.register_intent(skeleton_intent, self.handle_skeleton_filter_intent)

        detail_intent = IntentBuilder("DetailFilterIntent"). \
            require("DetailKeyword").build()

        self.register_intent(detail_intent, self.handle_detail_filter_intent)

        thresh_intent = IntentBuilder("ThreshFilterIntent"). \
            require("ThreshKeyword").build()

        self.register_intent(thresh_intent, self.handle_threshold_filter_intent)

        no_filter_intent = IntentBuilder("NoFilterIntent"). \
            require("NoFilterKeyword").build()

        self.register_intent(no_filter_intent, self.handle_no_filter_intent)

        webcam_intent = IntentBuilder("WebcamIntent"). \
            require("WebcamKeyword").build()

        self.register_intent(webcam_intent, self.handle_webcam_intent)

    def init_vision(self):
        self.set_default_context()
        # read cascades
        self.log.info("reading haar cascades")
        self.face_cascade = cv2.CascadeClassifier(dirname(__file__) + '/cascades/haarcascade_frontalface_alt2.xml')
        self.smile_cascade = cv2.CascadeClassifier(dirname(__file__) + '/cascades/haarcascade_smile.xml')
        self.leye_cascade = cv2.CascadeClassifier(dirname(__file__) + '/cascades/haarcascade_lefteye.xml')
        self.reye_cascade = cv2.CascadeClassifier(dirname(__file__) + '/cascades/haarcascade_righteye.xml')
        self.profileface_cascade = cv2.CascadeClassifier(dirname(__file__) + '/cascades/lbpcascade_profileface.xml')

        #######video streaming and fps ###########33
        self.log.info("initializing videostream")
        self.vs = eye(src=0).start()
        self.fps = FPS().start()

        # TODO distance from cam
        self.rect = (161, 79, 150, 150)  # random initial guess for foreground/face position for background extraction
        self.distance = 0
        # initialize the known distance from the camera to the reference eye pic, which
        # in this case is 50cm from computer screen
        self.KNOWN_DISTANCE = 50.0
        # initialize the known object width, which in this case, the human eye is 24mm width average
        self.KNOWN_WIDTH = 2.4
        # initialize the reference eye image that we'll be using
        self.REF_IMAGE_PATH = dirname(__file__) + "/ref/eye.jpg"
        # load the image that contains an eye that is KNOWN TO BE 50cm
        # from our camera, then find the eye marker in the image, and initialize
        # the focal length
        image = cv2.imread(self.REF_IMAGE_PATH)
        self.radius = 24  # initialize radius for distance counter
        marker = self.find_eye_radius(image)
        # calculate camera focallenght
        self.focalLength = (marker * self.KNOWN_DISTANCE) / self.KNOWN_WIDTH

        # TODO read from config file
        # bools
        self.showfeed = True
        self.showboundingboxes = True
        self.showdetected = True

        ######## detected objects ######
        self.detectedfaces = []
        self.detectedmoods = []

        # process first frame
        self.feed = self.process_frame()

        self.awake = True
        if self.awake:
            pass
            # TODO start vision thread
        self.filter = "None"

    def emit_result(self, path, server=False):
        requester = "vision_service"
        message_type = "vision_result"
        message_data = {"movement": self.movement, "master": self.master, "distance": self.distance,
                        "num_persons": self.num_persons, "smile_detected": self.smiling}
        message_data["file"] = path
        if server:
            # send server a message
            stype = "file"
            self.emitter.emit(Message("server_request",
                                      {"server_msg_type": stype, "requester": requester, "message_type": message_type,
                                       "message_data": message_data}, self.context))
        self.emitter.emit(Message(message_type, message_data, self.context))

    def handle_vision_request(self, message):
        self.process_frame()
        path = self.save_feed(self.webcam_path + "/" + asctime().replace(" ", "_") + ".jpg")
        source = message.context.get("source")
        if source is not None and "server" in source:
            self.emit_result(path, True)
        else:
            self.emit_result(path, False)


    # intents
    def handle_webcam_intent(self, message):
        self.process_frame()
        self.speak_dialog("webcam")
        path = self.save_feed(self.webcam_path+"/"+asctime()+".jpg")
        self.emit_result(path, False)
        #self.display_service.show(path)

    def handle_vision_data_intent(self, message):
        self.process_frame()
        self.speak("There are " + str(self.num_persons) + " persons on view")
        self.emit_result(path, False)
        # TODO more context, movement, face recog

    def handle_reset_vision_intent(self, message):
        self.speak_dialog("reset.vision")
        self.stop()
        self.init_vision()

    def handle_what_do_you_see_intent(self, message):
        self.process_frame()
        path = self.save_feed()
        #self.display_service.show(feed_path)
        self.speak_dialog("vision")
        self.emit_result(path, False)

    def handle_describe_what_do_you_see_intent(self, message):
        self.process_frame()
        feed_path = self.save_feed()
        self.emit_result(feed_path, False)
        classifier = ImageRecognitionService(self.emitter)
        results = classifier.server_image_classification(feed_path, self.context)
        i = 0
        for result in list(results):
            # cleave first word nxxxxx
            result = result.split(" ")[1:]
            r = ""
            for word in result:
                r += word + " "
            result = r[:-1].split(",")[0]
            results[i] = result
            i += 1

        self.speak("i see " + results[0] + ", or maybe it is " + results[1])

    def handle_skeleton_filter_intent(self, message):
        self.speak_dialog("skeleton")
        self.filter = "skeleton"

    def handle_detail_filter_intent(self, message):
        self.speak_dialog("detail")
        self.filter = "detail"

    def handle_smooth_filter_intent(self, message):
        self.speak_dialog("smooth")
        self.filter = "smooth"

    def handle_threshold_filter_intent(self, message):
        self.speak_dialog("thresh")
        self.filter = "thresh"

    def handle_no_filter_intent(self, message):
        self.speak_dialog("no.filter")
        self.filter = "None"

    def stop(self):
        self.fps.stop()
        self.log.info("elasped time: {:.2f}".format(self.fps.elapsed()))
        self.log.info("[INFO] approx. FPS: {:.2f}".format(self.fps.fps()))
        self.vs.stop()
        cv2.destroyAllWindows()

    # vision
    def save_feed(self, path=dirname(__file__) + "/feed.jpg"):
        try:
            if self.filter == "skeleton":
                self.feed = self.skeletonize(self.feed)
            elif self.filter == "thresh":
                self.feed = self.tresholdify(self.feed)
            elif self.filter == "smooth":
                self.feed = self.smothify(self.feed)
            elif self.filter == "detail":
                self.feed = self.detail_enhance(self.feed)
            elif self.filter == "cartoon":
                #self.feed = self.cartoonify(self.feed)
                pass
            elif self.filter == "pencil":
                #self.feed = self.pencil(self.feed)
                pass
        except:
            self.log.error("Error applying filter: " + self.filter)

        cv2.imwrite(path, self.feed)
        return path

    def vision_thread(self, show=False):
        while 1:
            self.feed = self.process_frame()
            if show:
                self.log.info("updating feed")
                #self.display_service.show(self.save_feed())
                cv2.waitKey(10)
            # wait for quit key - esc or q
            k = cv2.waitKey(100) & 0xff
            if k == 27 or k == ord('q'):
                break
        self.stop()

    def process_frame(self):
        self.log.debug(' grabing frame from camera ')
        img = self.vs.read()
        self.fps.update()
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

        # reset detected users
        face_counter = 0
        if len(self.detectedfaces) >= 1:
            for i in self.detectedfaces:
                self.detectedfaces.pop()

        if len(self.detectedmoods) >= 1:
            for i in self.detectedmoods:
                self.detectedmoods.pop()
        self.distance = 0
        self.set_default_context()  # no users

        # detect faces
        faces = self.find_faces(gray)
        sidefaces = self.find_side_faces(gray)
        biggest = 0

        self.log.debug(' searching for faces ')
        for (x, y, w, h) in faces:
            self.log.debug(' detected face id: ' + str(face_counter))
            roi_gray = gray[y:y + h, x:x + w]
            roi_color = img[y:y + h, x:x + w]

            # resize all faces to standard size and append to detected users
            resized_roi_color = cv2.resize(roi_color, (50, 50))
            self.detectedfaces.append(resized_roi_color)

            # find eyes
            self.log.debug(' searching for eyes ')
            reye, leye = self.find_eyes(roi_color)

            # crop eye pic
            eyepic = roi_color[leye[1]:leye[1] + leye[3], leye[0]:leye[0] + leye[2]]

            # calculate distance from camera by iris size
            self.distance = self.distance_from_cam(self.find_eye_radius(eyepic))

            # find smiles / primitive emotion tracking
            happy = False
            smiles = []
            # detect smile
            self.log.debug(' searching for smiles ')
            for (sx, sy, sw, sh) in self.find_smile(roi_gray):
                smiles.append((sx, sy, sw, sh))
                # draw bounding boxes
                if self.showboundingboxes:
                    cv2.rectangle(roi_color, (sx, sy), (sx + sw, sy + sh), (255, 255, 0), 2)

            if self.showboundingboxes:
                cv2.rectangle(roi_color, (leye[0], leye[1]), (leye[0] + leye[3], leye[1] + leye[2]), (0, 255, 0), 2)
                cv2.rectangle(roi_color, (reye[0], reye[1]), (reye[0] + reye[3], reye[1] + reye[2]), (0, 255, 255), 2)
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            # set happy flag
            if len(smiles) >= 1:
                happy = True

            # append mood info
            self.detectedmoods.append(happy)

            # TODO reocgnize face owner

            if w * h >= biggest:  # user detected
                biggest = w * h
                # foreground/focus rect = user face
                self.rect = (x, y, w, h)
                # update context
                self.update_context(face_counter)

        self.log.debug(' searching for profile faces ')
        for (x, y, w, h) in sidefaces:
            roi_gray = gray[y:y + h, x:x + w]
            roi_color = img[y:y + h, x:x + w]

            # resize all faces to standard size and append to detected users
            resized_roi_color = cv2.resize(roi_color, (50, 50))
            self.detectedfaces.append(resized_roi_color)

            if w * h >= biggest:  # user detected
                biggest = w * h
                # foreground/focus rect = user face
                self.rect = (x, y, w, h)
                # update context
                self.update_context(face_counter)

        self.log.info(' vision processing complete ')
        return img

    def find_faces(self, gray):
        # find faces in grayscale picture and return bounding boxes
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        # TODO add code to filter same face detected more than once?
        return faces

    def find_side_faces(self, gray):
        faces = self.profileface_cascade.detectMultiScale(gray, 1.3, 5)
        # add code to filter same face detected more than once
        return faces

    def find_smile(self, gray):
        # find smiles in grayscale picture and return bounding boxes
        smiles = self.smile_cascade.detectMultiScale(gray, 3, 12)
        # add code to filter same smile detected more than once
        return smiles

    def find_eyes(self, face):
        # find right and left eye in grayscale picture and return bounding rects
        reyes = self.reye_cascade.detectMultiScale(face, 1.3, 3)
        leyes = self.leye_cascade.detectMultiScale(face, 1.3, 3)
        # correct for multiple eyes
        # initialize eye position
        rx = 200
        lx, ry, rw, rh, ly, lw, lh = 0 , 0 ,0 ,0 ,0 ,0,0

        # pick right eye
        for (ex, ey, ew, eh) in reyes:
            if ex < rx:
                rx = ex
                ry = ey
                rw = ew
                rh = eh
        reye = (rx, ry, rw, rh)

        # pick left eye
        for (lex, ley, lew, leh) in leyes:
            if lex > lx:
                lx = lex
                ly = ley
                lw = lew
                lh = leh
        leye = (lx, ly, lw, lh)
        return reye, leye

    def distance_from_cam(self, rad):
        self.log.info("Calculating eye distance from camera")
        # calculate distance from camera from iris radius
        distance = (self.KNOWN_WIDTH * self.focalLength) / rad
        return distance

    def find_eye_radius(self, eye):
        self.log.info("measuring eye radius")
        # gray = cv2.cvtColor(eye, cv2.COLOR_BGR2GRAY)
        # gray = cv2.GaussianBlur(gray, (5, 5), 0)

        # param_1 = 200: Upper threshold for the internal Canny edge detector
        # param_2 = 100*: Threshold for center detection.
        # circles = cv2.HoughCircles(gray, cv2.cv.CV_HOUGH_GRADIENT, 1, 10,
        #                           param1=200, param2=100, minRadius=0, maxRadius=0)
        # if circles is not None:
        # circles = np.uint16(np.around(circles))
        # pick smallest circle works half time
        # pick centralish circle
        # minimum radus of 7 pixels
        #   for i in circles[0, :]:
        #     if i[2] < self.radius:
        #         x = i[0]
        #         y = i[1]
        #        self.radius = i[2]
        # draw
        #         cv2.circle(eye, (x, y), self.radius, (0, 255, 0), 2)
        # draw a dot on the circle (pupil)
        #        cv2.circle(eye, (x, y), 2, (0, 0, 255), 3)
        # k = cv2.waitKey(0)
        # print self.radius
        # cv2.imshow("eye", eye)
        return self.radius

    def remove_bkg(self, img):
        # quick sloppy background removal######
        self.log.info("removing background")
        #use grabcutwith facerecthas foreground
        mask = np.zeros(img.shape[:2], np.uint8)
        bgdModel = np.zeros((1, 65), np.float64)
        fgdModel = np.zeros((1, 65), np.float64)
        mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
        cv2.grabCut(img, mask, self.rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)
        img = img * mask2[:, :, np.newaxis]
        return img

    # vision context
    def set_default_context(self):
        # vision  processing
        self.master = False
        self.person_on_screen = False
        self.was_person_on_screen_before = False
        self.movement = False
        self.multiple_persons = False
        self.smiling = False
        self.distance = 0  # from camera
        self.num_persons = 0
        # vision data
        self.detectedfaces = []
        self.detectedsmiles = []
        # cv2 images
        self.mainface = None  # user face pic - biggest face rect if several faces
        self.lefteye = None
        self.righteye = None
        self.smile = None
        self.vision = None

    def update_context(self, faceid):
        self.log.info("updating context")
        if len(self.detectedfaces) >= 1:
            self.num_persons = len(self.detectedfaces)
            #detect if master
            self.master = False# implement face recognition first
            self.person_on_screen = True
            self.multiple_persons = True
            # save actual user face pic
            self.mainface = self.detectedfaces[faceid]
            # save smiling
            #self.smiling = self.detectedsmiles[faceid]
        else:
            self.person_on_screen = False
            self.multiple_persons = False
            self.smiling = False
            self.num_persons = 0

         #check if there were multiple users
        if len(self.detectedfaces) == 1:
            self.multiple_persons = False
        return

    # image filters
    def detail_enhance(self, pic):
        self.log.info("applying detail enhance filter")
        return cv2.detailEnhance(pic, sigma_s=10, sigma_r=0.15)

    def smothify(self, pic):
        self.log.info("applying smothify filter")
        return cv2.edgePreservingFilter(pic, flags=1, sigma_s=60, sigma_r=0.4)

    def skeletonize(self, pic):
        self.log.info("applying skeletonize filter")
        gray = cv2.cvtColor(pic, cv2.COLOR_BGR2GRAY)
        skelton = imutils.skeletonize(gray, size=(3, 3))
        return skelton

    def tresholdify(self, pic):
        self.log.info("applying threshold filter")
        pic = cv2.cvtColor(pic, cv2.COLOR_BGR2GRAY)
        pic = cv2.GaussianBlur(pic, (5, 5), 0)
        pic = cv2.adaptiveThreshold(pic, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 115, 1)
        return pic


def create_skill():
    return VisionSkill()


class ImageRecognitionService():
    def __init__(self, emitter, timeout=30, logger=None, server=False):
        self.emitter = emitter
        self.waiting = False
        self.server = server
        self.image_classification_result = {"classification":"unknown"}
        self.timeout = timeout
        if logger is not None:
            self.logger = logger
        else:
            self.logger = getLogger("ImageRecognitionService")

        self.emitter.on("image_classification_result", self.end_wait)

    def end_wait(self, message):
        if message.type == "image_classification_result":
            self.logger.info("image classification result received")
            self.image_classification_result = message.data
        self.waiting = False

    def wait(self):
        start = time.time()
        elapsed = 0
        self.waiting = True
        while self.waiting and elapsed < self.timeout:
            elapsed = time.time() - start
            time.sleep(0.1)

    def local_image_classification(self, picture_path, context=None):
        if context is None:
            context = {}
            requester = "vision_service"
        message_type = "image_classification_request"
        message_data = {"file": picture_path}
        self.emitter.emit(Message(message_type, message_data, context))
        self.wait()
        result = self.image_classification_result["classification"]
        return result

    def server_image_classification(self, picture_path, context=None):
        if context is None:
            context = {}
        # send server a message
        stype = "file"
        requester = "vision_service"
        message_type = "image_classification_request"
        message_data = {"file": picture_path}
        self.emitter.emit(Message("server_request",
                                  {"server_msg_type": stype, "requester": requester, "message_type": message_type,
                                   "message_data": message_data}, context))

        self.wait()
        result = self.image_classification_result["classification"]
        return result
