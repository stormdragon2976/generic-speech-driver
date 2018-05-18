#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2018, F123 Consulting, <information@f123.org>
# Copyright 2018, Storm Dragon, <storm_dragon@linux-a11y.org>
# Copyright 2018, Chrys <chrys@linux-a11y.org>
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3, or (at your option) any later
# version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this package; see the file COPYING.  If not, write to the Free
# Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA. 

# generic speech driver

from threading import Thread, Lock
from queue import Queue, Empty
import shlex
from subprocess import Popen
import time
from orca import chnames
from orca import debug
from orca import guilabels
from orca import messages
from orca import speechserver
from orca import settings
from orca import orca_state
from orca import punctuation_settings
from orca import settings_manager
                                                                                
_settingsManager = settings_manager.getManager()


class VoiceFamily(dict):
    """Holds the family description for a voice."""

    NAME   = "name"
    GENDER = "gender"
    LOCALE = "locale"
    DIALECT = "dialect"

    MALE   = "male"
    FEMALE = "female"

    settings = {
        NAME   : None,
        GENDER : None,
        LOCALE : None,
        DIALECT: None,
    }

    def __init__(self, props):
        """Create and initialize VoiceFamily."""
        self.genericDriver = driver()
        dict.__init__(self)

        self.update(VoiceFamily.settings)
        if props:
            self.update(props)

class SayAllContext:

    PROGRESS    = 0
    INTERRUPTED = 1
    COMPLETED   = 2

    def __init__(self, obj, utterance, startOffset=-1, endOffset=-1):
        """Creates a new SayAllContext that will be passed to the
        SayAll callback handler for progress updates on speech.
        If the object does not have an accessible text specialization,
        then startOffset and endOffset parameters are meaningless.
        If the object does have an accessible text specialization,
        then values >= 0 for startOffset and endOffset indicate
        where in the text the utterance has come from.

        Arguments:
        -obj:         the Accessible being spoken
        -utterance:   the actual utterance being spoken
        -startOffset: the start offset of the Accessible's text
        -endOffset:   the end offset of the Accessible's text
        """
        self.obj           = obj
        self.utterance     = utterance
        self.startOffset   = startOffset
        self.currentOffset = startOffset
        self.endOffset     = endOffset


class SpeechServer(object):
    """Provides speech server abstraction."""

    @staticmethod
    def getFactoryName():
        """Returns a localized name describing this factory."""
        return "generic speech driver"

    @staticmethod
    def getSpeechServers():
        """Gets available speech servers as a list.  The caller
        is responsible for calling the shutdown() method of each
        speech server returned.
        """
        return "Generic speech driver"

    @staticmethod
    def getSpeechServer(info):
        """Gets a given SpeechServer based upon the info.
        See SpeechServer.getInfo() for more info.
        """
        return "Generic speech driver"

    @staticmethod
    def shutdownActiveServers():
        """Cleans up and shuts down this factory.
        """
        self.genericDriver.shutdown()

    def __init__(self):
        pass

    def getInfo(self):
        """Returns [name, id]
        """
        return "Generic speech driver"

    def getVoiceFamilies(self):
        """Returns a list of VoiceFamily instances representing all
        voice families known by the speech server."""
        return "Generic speech driver"

    def speakCharacter(self, character, acss=None):
        """Speaks a single character immediately.

        Arguments:
        - character: text to be spoken
        - acss:      acss.ACSS instance; if None,
                     the default voice settings will be used.
                     Otherwise, the acss settings will be
                     used to augment/override the default
                     voice settings.
        """
        self.genericDriver.speak(character)

    def speakKeyEvent(self, event, acss=None):
        """Speaks a key event immediately.

        Arguments:
        - event: the input_event.KeyboardEvent.
        """
        self.genericDriver.speak(event)

    def speakUtterances(self, utteranceList, acss=None, interrupt=True):
        """Speaks the given list of utterances immediately.

        Arguments:
        - utteranceList: list of strings to be spoken
        - acss:      acss.ACSS instance; if None,
                     the default voice settings will be used.
                     Otherwise, the acss settings will be
                     used to augment/override the default
                     voice settings.
        - interrupt: if True, stop any speech currently in progress.
        """
        self.genericDriver.speak(utteranceList)

    def speak(self, text=None, acss=None, interrupt=True):
        """Speaks all queued text immediately.  If text is not None,
        it is added to the queue before speaking.

        Arguments:
        - text:      optional text to add to the queue before speaking
        - acss:      acss.ACSS instance; if None,
                     the default voice settings will be used.
                     Otherwise, the acss settings will be
                     used to augment/override the default
                     voice settings.
        - interrupt: if True, stops any speech in progress before
                     speaking the text
        """
        return self.genericDriver.speak()

    def isSpeaking(self):
        """"Returns True if the system is currently speaking."""
        return False

    def sayAll(self, utteranceIterator, progressCallback):
        """Iterates through the given utteranceIterator, speaking
        each utterance one at a time.  Subclasses may postpone
        getting a new element until the current element has been
        spoken.

        Arguments:
        - utteranceIterator: iterator/generator whose next() function
                             returns a [SayAllContext, acss] tuple
        - progressCallback:  called as speech progress is made - has a
                             signature of (SayAllContext, type), where
                             type is one of PROGRESS, INTERRUPTED, or
                             COMPLETED.
        """
        pass

    def increaseSpeechRate(self, step=5):
        """Increases the speech rate.
        """
        pass

    def decreaseSpeechRate(self, step=5):
        """Decreases the speech rate.
        """
        pass

    def increaseSpeechPitch(self, step=0.5):
        """Increases the speech pitch.
        """
        pass

    def decreaseSpeechPitch(self, step=0.5):
        """Decreases the speech pitch.
        """
        pass

    def updateCapitalizationStyle(self):
        """Updates the capitalization style used by the speech server."""
        pass

    def updatePunctuationLevel(self):
        """Punctuation level changed, inform this speechServer."""
        pass

    def stop(self):
        """Stops ongoing speech and flushes the queue."""
        self.generidDriver.stop()

    def shutdown(self):
        """Shuts down the speech engine."""
        self.genericDriver.shutdown()

    def reset(self, text=None, acss=None):
        """Resets the speech engine."""
        pass
class speakQueue(Queue):
    def clear(self):
        try:
            while True:
                self.get_nowait()
        except Empty:
            pass

class driver():
    def __init__(self):
        self.proc = None
        self.speechThread = Thread(target=self.worker)
        self.lock = Lock()
        self.textQueue = speakQueue()
        self.initialize()
    def initialize(self):
        environment = {'minVolume': 0,
                    'volume': '100',
                    'maxVolume': 200,
                    'minPitch': '0',
                    'pitch': '50',
                    'maxPitch': 99,
                    'minRate': 80,
                    'rate': '280',
                    'maxRate': 450,
                    'language': '',
                    'module': 'espeak',
                    'voice': 'en-us',
                    'command': 'espeak -a fenrirVolume -s fenrirRate -p fenrirPitch -v fenrirVoice -- "fenrirText"'
                   }
        self.env = environment  
        self.minVolume = self.env['minVolume']
        self.volume = self.env['volume']
        self.maxVolume = self.env['maxVolume']
        self.minPitch = self.env['minPitch']
        self.pitch = self.env['pitch']
        self.maxPitch = self.env['maxPitch']
        self.minRate = self.env['minRate']
        self.rate = self.env['rate']
        self.maxRate = self.env['maxRate']
        self.language = self.env['language']
        self.voice = self.env['voice']
        self.module = self.env['module']
        
        self.speechCommand = self.env['command']
        if self.speechCommand == '':
            self.speechCommand = 'espeak -a fenrirVolume -s fenrirRate -p fenrirPitch -v fenrirVoice -- "fenrirText"'           
        self._isInitialized = True   
        if self._isInitialized:
            self.speechThread.start()   
    def shutdown(self):
        if not self._isInitialized:
            return
        self.cancel()    
        self.textQueue.put(-1)

    def speak(self,text, queueable=True):
        if not self._isInitialized:
            return
        if not queueable: 
            self.cancel()        
        utterance = {
          'text': text,
          'volume': self.volume,
          'rate': self.rate,
          'pitch': self.pitch,
          'module': self.module,
          'language': self.language,
          'voice': self.voice,
        }    
        self.textQueue.put(utterance.copy())

    def cancel(self):
        if not self._isInitialized:
            return
        self.clear_buffer()
        self.lock.acquire(True)
        if self.proc:
            try:
                self.proc.terminate()
            except Exception as e:
                try:
                    self.proc.kill()
                except Exception as e:
                    pass
            self.proc = None            
        self.lock.release()
    def setCallback(self, callback):
        print('SpeechDummyDriver: setCallback')    

    def clear_buffer(self):
        if not self._isInitialized:
            return
        self.textQueue.clear()     
    
    def setVoice(self, voice):
        if not self._isInitialized:
            return
        self.voice = str(voice)

    def setPitch(self, pitch):
        if not self._isInitialized:
            return
        self.pitch = str(self.minPitch + pitch * (self.maxPitch - self.minPitch ))

    def setRate(self, rate):
        if not self._isInitialized:
            return
        self.rate = str(self.minRate + rate * (self.maxRate - self.minRate ))

    def setModule(self, module):
        if not self._isInitialized:
            return 
        self.module = str(module)

    def setLanguage(self, language):
        if not self._isInitialized:
            return
        self.language = str(language)

    def setVolume(self, volume):
        if not self._isInitialized:
            return     
        self.volume = str(self.minVolume + volume * (self.maxVolume - self.minVolume ))
    
    def worker(self):
        while True:
            utterance = self.textQueue.get()

            if isinstance(utterance, int):
                if utterance == -1:
                    return
                else:
                    continue
            elif not isinstance(utterance, dict):
                continue
            # no text means nothing to speak
            if not 'text' in utterance:
                continue
            if not isinstance(utterance['text'],str):
                continue            
            if utterance['text'] == '':
                continue
            # check for valid data fields
            if not 'volume' in utterance:
                utterance['volume'] = ''
            if not isinstance(utterance['volume'],str):
                utterance['volume'] = ''
            if not 'module' in utterance:
                utterance['module'] = ''
            if not isinstance(utterance['module'],str):
                utterance['module'] = ''
            if not 'language' in utterance:
                utterance['language'] = ''
            if not isinstance(utterance['language'],str):
                utterance['language'] = ''
            if not 'voice' in utterance:
                utterance['voice'] = ''
            if not isinstance(utterance['voice'],str):
                utterance['voice'] = ''
            if not 'pitch' in utterance:
                utterance['pitch'] = ''
            if not isinstance(utterance['pitch'],str):
                utterance['pitch'] = ''
            if not 'rate' in utterance:
                utterance['rate'] = ''
            if not isinstance(utterance['rate'],str):
                utterance['rate'] = ''

            popenSpeechCommand = shlex.split(self.speechCommand)

            for idx, word in enumerate(popenSpeechCommand):
                word = word.replace('fenrirVolume', str(utterance['volume'] ))
                word = word.replace('genericSpeechVolume', str(utterance['volume'] ))
                word = word.replace('fenrirModule', str(utterance['module']))
                word = word.replace('genericSpeechModule', str(utterance['module']))
                word = word.replace('fenrirLanguage', str(utterance['language']))
                word = word.replace('genericSpeechLanguage', str(utterance['language']))
                word = word.replace('fenrirVoice', str(utterance['voice']))
                word = word.replace('genericSpeechVoice', str(utterance['voice']))
                word = word.replace('fenrirPitch', str(utterance['pitch']))
                word = word.replace('genericSpeechPitch', str(utterance['pitch']))
                word = word.replace('fenrirRate', str(utterance['rate']))
                word = word.replace('genericSpeechRate', str(utterance['rate']))
                word = word.replace('fenrirText', str(utterance['text']))
                word = word.replace('genericSpeechText', str(utterance['text']))
                popenSpeechCommand[idx] = word
            try:
                self.lock.acquire(True)
                self.proc = Popen(popenSpeechCommand, stdin=None, stdout=None, stderr=None, shell=False)
                self.lock.release()	
                self.proc.wait()
            except Exception as e:
                print(e)

            self.lock.acquire(True)
            self.proc = None
            self.lock.release()

# create driver object
speechserver = driver()
# speak
speechserver.speak("For my frind storm, because he rulz")
# wait
time.sleep(1.6)
# stop worker
speechserver.shutdown()
