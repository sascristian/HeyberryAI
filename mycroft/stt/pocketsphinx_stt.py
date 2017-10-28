from speech_recognition import Recognizer, AudioData, RequestError, \
    PortableNamedTemporaryFile, UnknownValueError
from mycroft import MYCROFT_ROOT_PATH
import os


from pocketsphinx import pocketsphinx, Jsgf, FsgModel


class PS_Recognizer(Recognizer):
    def __init__(self, language="en-US", language_directory=None,
                 acoustic_parameters_directory=None,
                 language_model_file=None, phoneme_dictionary_file=None):
        super(PS_Recognizer, self).__init__()
        language = language.lower()
        language_directory = language_directory or os.path.join(
            MYCROFT_ROOT_PATH, "mycroft/client/speech/recognizer/model",
            language)
        if not os.path.isdir(language_directory):
            raise RequestError(
                "missing PocketSphinx language data directory: \"{}\"".format(
                    language_directory))

        acoustic_parameters_directory = acoustic_parameters_directory or  \
                                        os.path.join(language_directory,
                                                     "hmm")
        if not os.path.isdir(acoustic_parameters_directory):
            raise RequestError(
                "missing PocketSphinx language model parameters directory: \"{}\"".format(
                    acoustic_parameters_directory))

        language_model_file = language_model_file or os.path.join(
            language_directory, language + ".lm")
        if not os.path.isfile(language_model_file):
            raise RequestError(
                "missing PocketSphinx language model file: \"{}\"".format(
                    language_model_file))

        phoneme_dictionary_file = phoneme_dictionary_file or os.path.join(
            language_directory, language + ".dict")
        if not os.path.isfile(phoneme_dictionary_file):
            raise RequestError(
                "missing PocketSphinx phoneme dictionary file: \"{}\"".format(
                    phoneme_dictionary_file))

        # create decoder object
        config = pocketsphinx.Decoder.default_config()
        config.set_string("-hmm",
                          acoustic_parameters_directory)  # set the path of the hidden Markov model (HMM) parameter files
        config.set_string("-lm", language_model_file)
        config.set_string("-dict", phoneme_dictionary_file)
        config.set_string("-logfn",
                          os.devnull)  # disable logging (logging causes unwanted output in terminal)
        self.decoder = pocketsphinx.Decoder(config)
        self.lang = language

    def recognize(self, audio_data, keyword_entries=None, grammar=None):
        """
        Performs speech recognition on ``audio_data`` (an ``AudioData`` instance), using CMU Sphinx.
        The recognition language is determined by ``language``, an RFC5646 language tag like ``"en-US"`` or ``"en-GB"``, defaulting to US English. Out of the box, only ``en-US`` is supported. See `Notes on using `PocketSphinx <https://github.com/Uberi/speech_recognition/blob/master/reference/pocketsphinx.rst>`__ for information about installing other languages. This document is also included under ``reference/pocketsphinx.rst``.
        If specified, the keywords to search for are determined by ``keyword_entries``, an iterable of tuples of the form ``(keyword, sensitivity)``, where ``keyword`` is a phrase, and ``sensitivity`` is how sensitive to this phrase the recognizer should be, on a scale of 0 (very insensitive, more false negatives) to 1 (very sensitive, more false positives) inclusive. If not specified or ``None``, no keywords are used and Sphinx will simply transcribe whatever words it recognizes. Specifying ``keyword_entries`` is more accurate than just looking for those same keywords in non-keyword-based transcriptions, because Sphinx knows specifically what sounds to look for.
        Sphinx can also handle FSG or JSGF grammars. The parameter ``grammar`` expects a path to the grammar file. Note that if a JSGF grammar is passed, an FSG grammar will be created at the same location to speed up execution in the next run. If ``keyword_entries`` are passed, content of ``grammar`` will be ignored.
        Returns the most likely transcription if ``show_all`` is false (the default). Otherwise, returns the Sphinx ``pocketsphinx.pocketsphinx.Decoder`` object resulting from the recognition.
        Raises a ``speech_recognition.UnknownValueError`` exception if the speech is unintelligible. Raises a ``speech_recognition.RequestError`` exception if there are any issues with the Sphinx installation.
        """
        language = self.lang
        assert isinstance(audio_data,
                          AudioData), "``audio_data`` must be audio data"
        assert isinstance(language, str), "``language`` must be a string"
        assert keyword_entries is None or all(
            isinstance(keyword,
                       (type(""), type(u""))) and 0 <= sensitivity <= 1
            for keyword, sensitivity in
            keyword_entries), "``keyword_entries`` must be ``None`` or a list of pairs of strings and numbers between 0 and 1"

        # obtain audio data
        raw_data = audio_data.get_raw_data(convert_rate=16000,
                                           convert_width=2)  # the included language models require audio to be 16-bit mono 16 kHz in little-endian format

        # obtain recognition results
        if keyword_entries is not None:  # explicitly specified set of keywords
            with PortableNamedTemporaryFile("w") as f:
                # generate a keywords file - Sphinx documentation recommendeds sensitivities between 1e-50 and 1e-5
                f.writelines(
                    "{} /1e{}/\n".format(keyword, 100 * sensitivity - 110) for
                    keyword, sensitivity in keyword_entries)
                f.flush()

                # perform the speech recognition with the keywords file (this is inside the context manager so the file isn;t deleted until we're done)
                self.decoder.set_kws("keywords", f.name)
                self.decoder.set_search("keywords")
                self.decoder.start_utt()  # begin utterance processing
                self.decoder.process_raw(raw_data, False,
                                    True)  # process audio data with recognition enabled (no_search = False), as a full utterance (full_utt = True)
                self.decoder.end_utt()  # stop utterance processing
        elif grammar is not None:  # a path to a FSG or JSGF grammar
            if not os.path.exists(grammar):
                raise ValueError(
                    "Grammar '{0}' does not exist.".format(grammar))
            grammar_path = os.path.abspath(os.path.dirname(grammar))
            grammar_name = os.path.splitext(os.path.basename(grammar))[0]
            fsg_path = "{0}/{1}.fsg".format(grammar_path, grammar_name)
            if not os.path.exists(
                    fsg_path):  # create FSG grammar if not available
                jsgf = Jsgf(grammar)
                rule = jsgf.get_rule("{0}.{0}".format(grammar_name))
                fsg = jsgf.build_fsg(rule, self.decoder.get_logmath(), 7.5)
                fsg.writefile(fsg_path)
            else:
                fsg = FsgModel(fsg_path, self.decoder.get_logmath(), 7.5)
            self.decoder.set_fsg(grammar_name, fsg)
            self.decoder.set_search(grammar_name)
            self.decoder.start_utt()
            self.decoder.process_raw(raw_data, False,
                                True)  # process audio data with recognition enabled (no_search = False), as a full utterance (full_utt = True)
            self.decoder.end_utt()  # stop utterance processing
        else:  # no keywords, perform freeform recognition
            self.decoder.start_utt()  # begin utterance processing
            self.decoder.process_raw(raw_data, False,
                                True)  # process audio data with recognition enabled (no_search = False), as a full utterance (full_utt = True)
            self.decoder.end_utt()  # stop utterance processing

        # return results
        hypothesis = self.decoder.hyp()
        if hypothesis is not None: return hypothesis.hypstr
        raise UnknownValueError()  # no transcriptions available
