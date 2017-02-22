
from threading import Thread, Lock
import numpy as np
import cv2

from imutils.video import FPS
from imutils.video import WebcamVideoStream as eye
import imutils

from mycroft.context import VisionContext
from mycroft.messagebus.client.ws import WebsocketClient
from mycroft.messagebus.message import Message

#import userdetect
from time import gmtime, strftime
import time
from mycroft.util.log import getLogger

ctxtlogger = getLogger("Context")
logger = getLogger("Vision")
#ctxtlogger.setLevel('DEBUG')#comment line to enable logging

client = None
def connect():
    client.run_forever()


class OpticalNerve():

    def __init__(self):

        self.context = VisionContext("vision.context")
        self.context.setdefaultcontext()
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.line = cv2.LINE_AA
        ##############cascades##############
        logger.info("initializing haar cascades")
        # face_cascade = cv2.CascadeClassifier('cascades/lbpcascade_frontalface.xml')
        # face_cascade3 = cv2.CascadeClassifier('cascades/haarcascade_frontalface_default.xml')
        # face_cascade2 = cv2.CascadeClassifier('cascades/haarcascade_frontalface_alt.xml')
        self.face_cascade = cv2.CascadeClassifier('/home/user/mycroft-core/mycroft/OpticalNerve/cascades/haarcascade_frontalface_alt2.xml')
        self.smile_cascade = cv2.CascadeClassifier('/home/user/mycroft-core/mycroft/OpticalNerve/cascades/haarcascade_smile.xml')
        self.leye_cascade = cv2.CascadeClassifier('/home/user/mycroft-core/mycroft/OpticalNerve/cascades/haarcascade_lefteye.xml')
        self.reye_cascade = cv2.CascadeClassifier('/home/user/mycroft-core/mycroft/OpticalNerve/cascades/haarcascade_righteye.xml')
        self.profileface_cascade = cv2.CascadeClassifier('/home/user/mycroft-core/mycroft/OpticalNerve/cascades/lbpcascade_profileface.xml')

        #######video streaming and fps ###########33
        logger.info("initializing videostream")
        self.vs = eye(src=0 ).start()
        self.fps = FPS().start()
        self.rect = (161,79,150,150)#random initial guess for foreground/face position for background extraction
        self.distance = 0

        #face detector
        #self.faced = userdetect.UserDetect()
        # refactor this into a config file
        #bools
        self.showfeed = False
        self.showboundingboxes = True
        self.showdetected = True

        # initialize the known distance from the camera to the reference eye pic, which
        # in this case is 50cm from computer screen
        self.KNOWN_DISTANCE = 50.0
        # initialize the known object width, which in this case, the human eye is 24mm width average
        self.KNOWN_WIDTH = 2.4
        # initialize the reference eye image that we'll be using
        self.REF_IMAGE_PATH = "ref/eye.jpg"
        # load the image that contains an eye that is KNOWN TO BE 50cm
        # from our camera, then find the eye marker in the image, and initialize
        # the focal length
        image = cv2.imread(self.REF_IMAGE_PATH)
        self.radius = 24#initialize radius for distance counter
        marker = self.find_eye_radius(image)
        # calculate camera focallenght
        self.focalLength = (marker * self.KNOWN_DISTANCE) / self.KNOWN_WIDTH

        ######## detected objects ######
        self.detectedfaces = []
        self.detectedmoods = []
        logger.info("connecting to messagebus")
        #connect to messagebus
        global client
        client = WebsocketClient()

        def vision(message):
            if message.data.get('target') == "vision" or  message.data.get('target') == "all" :
                client.emit(
                    Message("vision_result",
                            {'asctime': time.asctime(),
                             'time': time.time(),
                             'movement': self.context.movement,
                             'number of persons': self.context.num_persons,
                             'master': self.context.master,
                             'smile detected ': self.context.smiling}))

        client.emitter.on("context_update", vision)
        event_thread = Thread(target=connect)
        event_thread.setDaemon(True)
        event_thread.start()

        # process first frame
        self.feed = self.readeye()


    def read(self):
        # return the context from frame most recently processed by the eye
        self.feed = self.readeye()
        self.context.read()
        return self.context, self.feed

    ######find faces in grayscale picture and return bounding boxes
    def find_faces(self, gray):
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        # add code to filter same face detected more than once
        return faces

    def find_side_faces(self, gray):
        faces = self.profileface_cascade.detectMultiScale(gray, 1.3, 5)
        # add code to filter same face detected more than once
        return faces
    ######find smiles in grayscale picture and return bounding boxes
    def find_smile(self, gray):
        smiles = self.smile_cascade.detectMultiScale(gray, 3, 12)
        # add code to filter same smile detected more than once
        return smiles

    ######find right and left eye in grayscale picture and return bounding rects
    def find_eye(self, face):

        reyes = self.reye_cascade.detectMultiScale(face, 1.3, 3)
        leyes = self.leye_cascade.detectMultiScale(face, 1.3, 3)
        ####correct for multiple eyes
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

    ###### TODO calculate distance from camera from iris radius
    def distance_from_cam(self, rad):
        distance = (self.KNOWN_WIDTH * self.focalLength) / rad
        return distance
        #########find eye radius from webcam region of interest ########

    def find_eye_radius(self, eye):
        logger.info("measuring eye radius")
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
        ####### select eye/region of interest from face, find eye radius, compute distance from camera #######

    def calculatedist(self, leye, face):
        logger.info("calculating distance from camera")
        ###select eye region
        eye = face[leye[1]:leye[1] + leye[3] * 1.5, leye[0]:leye[0] + leye[2] * 1.5]
        rad = 2 * self.find_eye_radius(eye)
        self.mdistance = self.distance_from_cam(rad)
        return self.mdistance

    ######quick sloppy background removal######
    def remove_bkg(self, img):
        logger.info("removing background")
        #use grabcutwith facerecthas foreground
        mask = np.zeros(img.shape[:2], np.uint8)
        bgdModel = np.zeros((1, 65), np.float64)
        fgdModel = np.zeros((1, 65), np.float64)
        mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
        cv2.grabCut(img, mask, self.rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)
        img = img * mask2[:, :, np.newaxis]
        return img

    ###### image filters#####
    #### cartoonify
    def cartoonify(self, pic):
        logger.info("applying cartoonify filter")
        return cv2.stylization(pic, sigma_s=60, sigma_r=0.07)
    ### nightmare
    def nightmarify(self, pic, bw=True):
        logger.info("applying nightmarify filter")
        nght_gray, nght_color = cv2.pencilSketch(pic, sigma_s=60, sigma_r=0.07, shade_factor=0.05)
        if bw:
            #nght_gray = cv2.cvtColor(nght_gray, cv2.COLOR_GRAY2BGR)
            return nght_gray
        return nght_color
    #### detail enhance
    def detail_enhance(self, pic):
        logger.info("applying detail enhance filter")
        return cv2.detailEnhance(pic, sigma_s=10, sigma_r=0.15)
    #### smothify
    def smothify(self, pic):
        logger.info("applying smothify filter")
        return cv2.edgePreservingFilter(pic, flags=1, sigma_s=60, sigma_r=0.4)
    #### skeletonize
    def skeletonize(self, pic):
        logger.info("applying skeletonize filter")
        gray = cv2.cvtColor(pic, cv2.COLOR_BGR2GRAY)
        skelton = imutils.skeletonize(gray, size=(3, 3))
        return skelton
    ###### tresh
    def tresholdify(self, pic):
        logger.info("applying threshold filter")
        pic = cv2.cvtColor(pic, cv2.COLOR_BGR2GRAY)
        pic = cv2.GaussianBlur(pic, (5, 5), 0)
        pic = cv2.adaptiveThreshold(pic, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 115, 1)
        return pic

    ##### read webcam
    def readeye(self):
        logger.debug(' grabing frame from camera ')
        img = self.vs.read()
        self.fps.update()
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

        #### reset detected users
        face_counter = 0
        if len(self.detectedfaces) >= 1:
            for i in self.detectedfaces:
                self.detectedfaces.pop()

        if len(self.detectedmoods) >= 1:
            for i in self.detectedmoods:
                self.detectedmoods.pop()
        self.distance = 0

        ##### detect faces
        faces = self.find_faces(gray)
        sidefaces = self.find_side_faces(gray)
        biggest = 0

        ctxtlogger.debug(' setting default context for vision processing: ')
        self.context.setdefaultcontext()#no users

        logger.debug(' searching for faces ')
        for (x, y, w, h) in faces:
            #logger.debug(' detected face id: ' + str(face_counter))
            roi_gray = gray[y:y + h, x:x + w]
            roi_color = img[y:y + h, x:x + w]

            # resize all faces to standard size and append to detected users
            # resized_roi_gray = cv2.resize(roi_gray, (20, 20))
            resized_roi_color = cv2.resize(roi_color, (50, 50))
            self.detectedfaces.append(resized_roi_color)

            # find eyes
            logger.debug(' searching for eyes ')
            reye, leye = self.find_eye(roi_color)

            # crop eye pic
            eyepic = roi_color[leye[1]:leye[1] + leye[3], leye[0]:leye[0] + leye[2]]

            # calculate distance from camera by iris size
            self.distance = self.distance_from_cam(self.find_eye_radius(eyepic))

            # print distance in feed
            ###primitive emotion tracking###
            happy = False
            smiles = []
            # detect smile
            logger.debug(' searching for smiles ')
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

            ### append mood info
            self.detectedmoods.append(happy)

            ####recognize face owner         dlib is not working on this computer
            # warped_im2=self.faced.align(roi_gray)
            # cv2.imwrite('result_align/' + str(face_counter) + '.jpg', warped_im2)

            if w * h >= biggest:  # user detected
                biggest = w * h
                # foreground/focus rect = user face
                self.rect = (x, y, w, h)
                # update context
                ctxtlogger.debug(' updating context for face detected: ')
                self.updatecontext(face_counter)

        logger.debug(' searching for profile faces ')
        for (x, y, w, h) in sidefaces:

            roi_gray = gray[y:y + h, x:x + w]
            roi_color = img[y:y + h, x:x + w]

            # resize all faces to standard size and append to detected users
            #resized_roi_gray = cv2.resize(roi_gray, (20, 20))
            resized_roi_color = cv2.resize(roi_color, (50, 50))
            self.detectedfaces.append(resized_roi_color)

            happy = False
            smiles = []
            # detect smile
            for (sx, sy, sw, sh) in self.find_smile(roi_gray):
                smiles.append((sx, sy, sw, sh))
                #draw bounding boxes
                if self.showboundingboxes:
                    cv2.rectangle(roi_color, (sx, sy), (sx + sw, sy + sh), (255, 255, 0), 2)

            if self.showboundingboxes:
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            #set happy flag
            if len(smiles) >= 1:
                happy = True

            ### append mood info
            self.detectedmoods.append(happy)

            ####recognize face owner         dlib is not working on this computer
            #warped_im2=self.faced.align(roi_gray)
            #cv2.imwrite('result_align/' + str(face_counter) + '.jpg', warped_im2)

            if w * h >= biggest:  # user detected
                biggest = w * h
                # foreground/focus rect = user face
                self.rect = (x, y, w, h)
                # update context
                ctxtlogger.debug(' updating context for face detected: ')
                self.updatecontext(face_counter)

        logger.info(' vision processing completed ')
        return img

    def draw_feeds(self, bkg, mainfeed):
        # The dimensions of the nkg picture
        #width, height, channels = bkg.shape

        #main feed in top eft corner, 1/2 of screen dedicated
        #mainfeed = cv2.resize(mainfeed, (width / 2, height / 2), interpolation=cv2.INTER_AREA)

        if self.showfeed:
            # draw feed
            cv2.imshow("feed", mainfeed)
            #cv2.imshow("nght", self.nightmarify(mainfeed))
            #bkg[0:height / 2, 0:width / 2] = mainfeed  # coordinates to draw into

        ## draw individual detected faces
       # if self.showdetected:
            # Detected Faces
        #    i = 1
         #   for face in self.detectedfaces:
          #      bkg[height/2: height/2 +50, i*50:i*50 + 50] = face
           #     i += 1
                # add user names and smiles
        return bkg

    def draw_gui_bkg(self):
        # Create a white image as placeholder
        bkg = np.zeros((800, 800, 3), np.uint8)
        ## create lines
        ## create text
        ## create settings scroll bars

        return bkg

    def updatecontext(self, faceid):
        logger.info("updating context")
        if len(self.detectedfaces) >= 1:
            self.context.timeuser = time.time()
            self.context.num_persons = len(self.detectedfaces)

            #detect if master
            self.context.master = False# implement face recognition first
            self.context.person_on_screen = True
            self.context.multiple_persons = True
            # save actual user face pic
            self.context.mainface = self.detectedfaces[faceid]
            # save smiling
            self.context.smiling = self.detectedmoods[faceid]
            # update time counter
            self.context.user_last_seen = strftime("%Y-%m-%d %H:%M:%S", gmtime())
            if self.context.master:
                self.context.master_last_seen = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        else:
            self.context.person_on_screen = False
            self.context.multiple_persons = False
            self.context.smiling = False
            self.context.num_persons = 0

         #check if there were multiple users
        if len(self.detectedfaces) == 1:
            self.context.multiple_persons = False

        #update distance
        self.context.distance = self.distance

        #save to disc
        self.context.update()

        return

    def vision_gui(self, show=True):
        ######### add code to check for instruction from AI message BUS if none default loop
        while 1:
            self.context.read()
            self.feed = self.readeye()
            if show:
                logger.info("updating feed")
                bkg = self.draw_gui_bkg()
                vision = self.draw_feeds(bkg, self.feed)
                #cv2.imshow("JArbas Vision", vision)
                cv2.waitKey(10)
                # emit to bus


            logger.info("movement: "+str(self.context.movement))
            logger.info('number of persons: '+str(self.context.num_persons))
            logger.info('master: '+str(self.context.master))
            logger.info('smile detected :'+str(self.context.smiling))
            # wait for quit key - esc or q
            k = cv2.waitKey(100) & 0xff
            if k == 27 or k == ord('q'):
                break
        self.stop()

    ###### stop face recognition #####
    def stop(self):
        self.fps.stop()
        logger.info("elasped time: {:.2f}".format(self.fps.elapsed()))
        logger.info("[INFO] approx. FPS: {:.2f}".format(self.fps.fps()))
        self.vs.stop()
        self.context.close()
        cv2.destroyAllWindows()


vision = OpticalNerve()
vision.vision_gui()
