#!/usr/bin/python
# -*- coding: utf-8 -*-

# generic speech driver

from threading import Thread, Lock
from queue import Queue, Empty
import shlex
from subprocess import Popen

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
                    'volume': 100,
                    'maxVolume': 200,
                    'minPitch': 0,
                    'pitch': 5,
                    'maxPitch': 99,
                    'minRate': 80,
                    'rate': 120,
                    'maxRate': 450,
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
                pass

            self.lock.acquire(True)
            self.proc = None
            self.lock.release()

speechserver = driver()
speechserver.speak("hello world")
time.sleep(3)
