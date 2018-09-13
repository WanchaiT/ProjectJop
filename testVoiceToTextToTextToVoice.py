# -*- coding: utf-8 -*-
"""
Created on Thu Sep  6 23:46:23 2018

@author: vento
"""
import moviepy.editor as mp
from pydub import AudioSegment
import speech_recognition as sr #Google Speech Recognition API : BSD license
from googletrans import Translator #Google Translate API : Free
from gtts import gTTS #Google TTS (Text-to-Speech) API  : License: MIT

def CutWaveFromVDO(pathV,pathW): #avi to wav
    clip = mp.VideoFileClip(pathV).subclip(0,-1)
    clip.audio.write_audiofile(pathW)

def Slice(inputAudio,output,start,end): #wav to wav
    start = int(start * 1000) #Works in milliseconds
    end = int(end * 1000)
    newAudio = inputAudio[start:end]
    newAudio.export(output, format="wav")


def VoiceToText(path,lang):# wav to string
    r = sr.Recognizer()
    with sr.WavFile(path) as source:             
        audio = r.record(source)                    
        try:
            return r.recognize_google(audio,language = lang)  
        except:                            
            return ''    

def TranSlateToThai(text): # string to string
    translator = Translator()
    try:
        t = translator.translate(text,'th')
        return t.text
    except:
        return ''

def TextToSpeechThai(Text,path): # string to mp3
    tts = gTTS(text=Text,lang='th') 
    tts.save(path)

def MP3toWAV(mp3Path,wavPath): # mp3 to wav
    sound = AudioSegment.from_mp3(mp3Path) 
    sound.export(wavPath, format="wav")
    
def SpeedChange(input,output,speed): #speed same original
    sound = AudioSegment.from_file(input)
    newSound = sound._spawn(sound.raw_data, overrides={
        "frame_rate": int(sound.frame_rate * speed)
    })
    newSound.export(output,format="wav")
    
def AudioConcat(path1,path2,pathOut): #wav + wav to wav
    sound1 = AudioSegment.from_wav(path1)
    sound2 = AudioSegment.from_wav(path2)
    combined_sounds = sound1 + sound2 + sound1
    combined_sounds.export(pathOut, format="wav")
    
def VdoMergeAudio(pathVdo,pathAudio,pathMix): #avi + wav to mp4
    audio = mp.AudioFileClip(pathAudio)
    video1 = mp.VideoFileClip(pathVdo)
    final = mp.concatenate_videoclips([video1]).set_audio(audio)
    final.write_videofile(pathMix)
    
#-------------------------------------------------------------------------------------------------------
pathInput = "C://Users//vento//Documents//Project//W4//" #"wt6.avi"
pathOutput = "C://Users//vento//Documents//Project//W4//" #wt6Dub.avi"

CutWaveFromVDO(pathInput+"wt6.avi",pathOutput+"wt6Wav.wav")                         # avi => wav

inputAudio = AudioSegment.from_wav(pathOutput+"wt6Wav.wav")                         
times = int(inputAudio.duration_seconds/4)

start = 0                                                                           # split wav 4 second
end = 4
for i in range(times):
    Slice(inputAudio,pathOutput+"w"+str(i)+".wav",start,end)
    start = end
    end = end + 4

del inputAudio
for i in range(times):                                                              # chunk : wav => text => text => mp3
    textKR = VoiceToText(pathOutput+"w"+str(i)+".wav","ko-KR")
    print(str(i)+" "+textKR)
    textThai = TranSlateToThai(textKR)
    print(str(i)+" "+textThai)
    if(textThai!=''):
         TextToSpeechThai(textThai,pathOutput+"w"+str(i)+"Tran.mp3")

for i in range(times):                                                              # chunk : mp3 => wav
    try:
        MP3toWAV(pathOutput+"w"+str(i)+"Tran.mp3",pathOutput+"w"+str(i)+".wav")
    except:
        print(str(i)+" use olds")

for i in range(times):                                                              # change duration to 4 sec
    audio = AudioSegment.from_wav(pathOutput+"w"+str(i)+".wav")    
    speed = audio.duration_seconds/4.0                                                    
    SpeedChange(pathOutput+"w"+str(i)+".wav",pathOutput+"w"+str(i)+".wav",speed)

sound = AudioSegment.from_wav(pathOutput+"w0.wav")                                  # group chunk wav => wav
for i in range(1,times):
    nextSound = AudioSegment.from_wav(pathOutput+"w"+str(i)+".wav")
    sound = sound + nextSound
sound.export(pathOutput+"wt6WavTran.wav", format="wav")

VdoMergeAudio(pathOutput+"wt6.avi",pathOutput+"wt6WavTran.wav",pathOutput+"wt6Tran.mp4")   # merge avi , wav => mp4
