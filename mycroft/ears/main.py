import sys, os, alsaaudio, time, audioop, numpy, glob, scipy, subprocess, wave, cPickle, threading, shutil, cv2

import matplotlib.pyplot as plt
import scipy.io.wavfile as wavfile
from scipy.fftpack import rfft
from pyAudioAnalysis import audioFeatureExtraction as aF
from pyAudioAnalysis import audioTrainTest as aT
from pyAudioAnalysis import audioSegmentation as aS
from scipy.fftpack import fft
import matplotlib
import scipy.signal
import itertools
import operator
import datetime
import signal

path = "/home/user/mycroft-core/mycroft/ears/"
class AudioAnalisys():
    def __init__(self):
        self.allData = []
        self.HeightPlot = 150
        self.WidthPlot = 720
        self.statusHeight = 150;
        self.minActivityDuration = 0.8
        self.Fs = 16000
        self.tresh = 1.2 #1.2 default

        signal.signal(signal.SIGINT, self.signal_handler)

       # aT.featureAndTrain(["classifierData/music", "classifierData/speech"], 1.0, 1.0, aT.shortTermWindow,
       #                    aT.shortTermStep, "svm", "svmSMtemp", False)


    def signal_handler(self, signal, frame):
        wavfile.write(path+"output.wav", self.Fs, numpy.int16(self.allData))  # write final buffer to wav file
        print('You pressed Ctrl+C!')
        sys.exit(0)

    def recordAudioSegments(self, BLOCKSIZE=0.1, showSpectrogram=True, showChromagram=True, recordActivity=True):
        print "Press Ctr+C to stop recording"

        startDateTimeStr = datetime.datetime.now().strftime("%Y_%m_%d_%I:%M%p")

        MEAN, STD = loadMEANS(path+"models/svmMovies8classesMEANS")  # load MEAN feature values

        inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NONBLOCK)  # open alsaaudio capture
        inp.setchannels(1)  # 1 channel
        inp.setrate(self.Fs)  # set sampling freq
        inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)  # set 2-byte sample
        inp.setperiodsize(512)
        midTermBufferSize = int(self.Fs * BLOCKSIZE)
        midTermBuffer = []
        curWindow = []
        count = 0
        self.allData = []
        energy100_buffer_zero = []
        curActiveWindow = numpy.array([])
        timeStart = time.time()

        while 1:
            l, data = inp.read()  # read data from buffer
            if l:
                for i in range(len(data) / 2):
                    curWindow.append(audioop.getsample(data, 2, i))  # get audio samples

                if (len(curWindow) + len(midTermBuffer) > midTermBufferSize):
                    samplesToCopyToMidBuffer = midTermBufferSize - len(midTermBuffer)
                else:
                    samplesToCopyToMidBuffer = len(curWindow)

                midTermBuffer = midTermBuffer + curWindow[0:samplesToCopyToMidBuffer];  # copy to midTermBuffer
                del (curWindow[0:samplesToCopyToMidBuffer])

                if len(midTermBuffer) == midTermBufferSize:  # if midTermBuffer is full:
                    elapsedTime = (time.time() - timeStart)  # time since recording started
                    dataTime = (count + 1) * BLOCKSIZE  # data-driven time

                    # TODO
                    # mtF, _ = aF.mtFeatureExtraction(midTermBuffer, self.Fs, BLOCKSIZE * self.Fs, BLOCKSIZE * self.Fs, 0.050 * self.Fs, 0.050 * self.Fs)
                    # curFV = (mtF - MEAN) / STD
                    # TODO
                    self.allData += midTermBuffer
                    midTermBuffer = numpy.double(midTermBuffer)  # convert current buffer to numpy array

                    # Compute spectrogram
                    if showSpectrogram:
                        (spectrogram, TimeAxisS, FreqAxisS) = aF.stSpectogram(midTermBuffer, self.Fs, 0.020 * self.Fs,
                                                                              0.02 * self.Fs)  # extract spectrogram
                        FreqAxisS = numpy.array(FreqAxisS)  # frequency axis
                        DominantFreqs = FreqAxisS[
                            numpy.argmax(spectrogram, axis=1)]  # most dominant frequencies (for each short-term window)
                        maxFreq = numpy.mean(DominantFreqs)  # get average most dominant freq
                        maxFreqStd = numpy.std(DominantFreqs)

                        # Compute chromagram
                    if showChromagram:
                        (chromagram, TimeAxisC, FreqAxisC) = aF.stChromagram(midTermBuffer, self.Fs, 0.020 * self.Fs,
                                                                             0.02 * self.Fs)  # get chromagram
                        FreqAxisC = numpy.array(FreqAxisC)  # frequency axis (12 chroma classes)
                        DominantFreqsC = FreqAxisC[numpy.argmax(chromagram, axis=1)]  # most dominant chroma classes
                        maxFreqC = most_common(DominantFreqsC)[0]  # get most common among all short-term windows

                    # Plot signal window
                    signalPlotCV = plotCV(scipy.signal.resample(midTermBuffer + 16000, self.WidthPlot), self.WidthPlot,
                                          self.HeightPlot,
                                          32000)
                    cv2.imshow('Signal', signalPlotCV)
                    cv2.moveWindow('Signal', 50, self.statusHeight + 50)

                    # Show spectrogram
                    if showSpectrogram:
                        iSpec = numpy.array(spectrogram.T * 255, dtype=numpy.uint8)
                        iSpec2 = cv2.resize(iSpec, (self.WidthPlot, self.HeightPlot), interpolation=cv2.INTER_CUBIC)
                        iSpec2 = cv2.applyColorMap(iSpec2, cv2.COLORMAP_JET)
                        cv2.putText(iSpec2, "maxFreq: %.0f Hz" % maxFreq, (0, 11), cv2.FONT_HERSHEY_PLAIN, 1,
                                    (200, 200, 200))
                        cv2.imshow('Spectrogram', iSpec2)
                        cv2.moveWindow('Spectrogram', 50, self.HeightPlot + self.statusHeight + 60)

                    # Show chromagram
                    if showChromagram:
                        iChroma = numpy.array((chromagram.T / chromagram.max()) * 255, dtype=numpy.uint8)
                        iChroma2 = cv2.resize(iChroma, (self.WidthPlot, self.HeightPlot), interpolation=cv2.INTER_CUBIC)
                        iChroma2 = cv2.applyColorMap(iChroma2, cv2.COLORMAP_JET)
                        cv2.putText(iChroma2, "maxFreqC: %s" % maxFreqC, (0, 11), cv2.FONT_HERSHEY_PLAIN, 1,
                                    (200, 200, 200))
                        cv2.imshow('Chroma', iChroma2)
                        cv2.moveWindow('Chroma', 50, 2 * self.HeightPlot + self.statusHeight + 60)

                    # Activity Detection:
                    energy100 = (100 * numpy.sum(midTermBuffer * midTermBuffer)
                                 / (midTermBuffer.shape[0] * 32000 * 32000))
                    if count < 10:  # TODO make this param
                        energy100_buffer_zero.append(energy100)
                        mean_energy100_zero = numpy.mean(numpy.array(energy100_buffer_zero))
                    else:
                        mean_energy100_zero = numpy.mean(numpy.array(energy100_buffer_zero))
                      #  print "current  "+str(energy100)
                      #  print "tresh  :"  + str(self.tresh * mean_energy100_zero)
                        if (energy100 < self.tresh * mean_energy100_zero):
                            if curActiveWindow.shape[0] > 0:  # if a sound has been detected in the previous segment:
                                activeT2 = elapsedTime - BLOCKSIZE  # set time of current active window
                                if activeT2 - activeT1 > self.minActivityDuration:
                                    wavFileName = startDateTimeStr + "_activity_{0:.2f}_{1:.2f}.wav".format(activeT1,
                                                                                                            activeT2)
                                    if recordActivity:
                                        wavfile.write(wavFileName, self.Fs,
                                                      numpy.int16(
                                                          curActiveWindow))  # write current active window to file
                                        ######## TODO identify detected sound
                                        self.idsound(wavFileName)
                                curActiveWindow = numpy.array([])  # delete current active window

                        else:
                            if curActiveWindow.shape[0] == 0:  # this is a new active window!
                                activeT1 = elapsedTime - BLOCKSIZE  # set timestamp start of new active window
                            curActiveWindow = numpy.concatenate((curActiveWindow, midTermBuffer))

                            # Show status messages on Status cv winow:
                    textIm = numpy.zeros((self.statusHeight, self.WidthPlot, 3))
                    statusStrTime = "time: %.1f sec" % elapsedTime + " - data time: %.1f sec" % dataTime + " - loss : %.1f sec" % (
                        elapsedTime - dataTime)
                    statusStrFeature = "ene1:%.1f" % energy100 + " eneZero:%.1f" % mean_energy100_zero
                    cv2.putText(textIm, statusStrTime, (0, 11), cv2.FONT_HERSHEY_PLAIN, 1, (200, 200, 200))
                    cv2.putText(textIm, statusStrFeature, (0, 22), cv2.FONT_HERSHEY_PLAIN, 1, (200, 200, 200))
                    if curActiveWindow.shape[0] > 0:
                        cv2.putText(textIm, "sound", (0, 33), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255))
                    else:
                        cv2.putText(textIm, "silence", (0, 33), cv2.FONT_HERSHEY_PLAIN, 1, (200, 200, 220))
                    cv2.imshow("Status", textIm)
                    cv2.moveWindow("Status", 50, 0)
                    midTermBuffer = []
                    ch = cv2.waitKey(10)
                    count += 1

    def idsound(self, filename):
        "svmSMtemp"
        #Results = []
        modelType = "knn"
        modelName = path+"models/knnMovies8classes"
        [Result, P, classNames] = aT.fileClassification(filename, modelName, modelType)
        i=0
        result2=1
        while i < len(P):
            if i != Result and P[i] > P[result2] and P[i] < P[Result]:
                result2 = i
            i += 1

        print "i think i just heard  " + classNames[Result]
        if result2 != Result:
            print "or maybe it was  " + classNames[result2]

        id1 = classNames[Result]
        id2 = classNames[result2]

        if id1 == "Music" or id2 == "Music":
            modelType = "knn"
            modelName = path+"models/knnMusicGenre6"
            [Result, P, classNames] = aT.fileClassification(filename, modelName, modelType)
            i = 0
            result2 = 1
            while i < len(P):
                if i != Result and P[i] > P[result2] and P[i] < P[Result]:
                    result2 = i
                i += 1

            print "i think i just heard  " + classNames[Result]
            if result2 != Result:
                print "or maybe it was  " + classNames[result2]

            style = classNames[Result]
            style2 = classNames[result2]
        #for i <:
        #    print classNames[i]
        #    print P[i]

       # Results = []
       # modelType = "svm"
       # modelName = "svmMovies8classes"
       # [Result, P, classNames] = aT.fileClassification(filename, modelName, modelType)
       # Result = int(Result)
       # Results.append(Result)
       # print "{0:s}\t{1:s}".format(filename, classNames[Result])
       # print P

       # modelType = "knn"
       # modelName = "knnMusicGenre6"
       # [Result, P, classNames] = aT.fileClassification(filename, modelName, modelType)
       # Result = int(Result)
       # Results.append(Result)
       # print "{0:s}\t{1:s}".format(filename, classNames[Result])
       # print P

       # modelType = "knn"
       # modelName = "knnMusicGenre3"
       # [Result, P, classNames] = aT.fileClassification(filename, modelName, modelType)
       # Result = int(Result)
       # Results.append(Result)
       # print "{0:s}\t{1:s}".format(filename, classNames[Result])
       # print P

        if id1 == "Speech" or id2 == "Speech":
            modelType = "knn"
            modelName = path+"models/knnSpeakerFemaleMale"
            [Result, P, classNames] = aT.fileClassification(filename, modelName, modelType)
            i = 0
            result2 = 1
            while i < len(P):
                if i != Result and P[i] > P[result2] and P[i] < P[Result]:
                    result2 = i
                i += 1

            print "i think i just heard  " + classNames[Result]
            gender = classNames[Result]

        os.remove(filename)

        #silence, noise, music, speech - music detected as screams
            #if speech male or female
            #elif music style
            #elif noise - level?
        pass

'''
Utitlity functions:
'''


def loadMEANS(modelName):
    # load pyAudioAnalysis classifier file (MEAN and STD values).
    # used for feature normalization
    try:
        fo = open(modelName, "rb")
    except IOError:
        print "Load Model: Didn't find file"
        return
    try:
        MEAN = cPickle.load(fo)
        STD = cPickle.load(fo)
    except:
        fo.close()
    fo.close()
    return (MEAN, STD)


def most_common(L):
    # get an iterable of (item, iterable) pairs
    SL = sorted((x, i) for i, x in enumerate(L))
    #print 'SL:', SL
    groups = itertools.groupby(SL, key=operator.itemgetter(0))

    # auxiliary function to get "quality" for an item
    def _auxfun(g):
        item, iterable = g
        count = 0
        min_index = len(L)
        for _, where in iterable:
            count += 1
            min_index = min(min_index, where)
        #print 'item %r, count %r, minind %r' % (item, count, min_index)
        return count, -min_index

    # pick the highest-count/earliest item
    return max(groups, key=_auxfun)[0]


def plotCV(Fun, Width, Height, MAX):
    if len(Fun) > Width:
        hist_item = Height * (Fun[len(Fun) - Width - 1:-1] / MAX)
    else:
        hist_item = Height * (Fun / MAX)
    h = numpy.zeros((Height, Width, 3))
    hist = numpy.int32(numpy.around(hist_item))

    for x, y in enumerate(hist):
        cv2.line(h, (x, Height / 2), (x, Height - y), (255, 0, 255))

    return h

#ears = AudioAnalisys()
#ears.recordAudioSegments()