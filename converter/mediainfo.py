# -*- coding: cp936 -*-
'''
Created on 2013-11-14

@author: hui.taoh
'''


import sys
import os
import subprocess
from pprint import pprint

MEDIAINFO='MediaInfo.x64.exe'

# Media has a container, and then video, audio and text streams

# Lines to parse
#General
#Format                           : Matroska
#Codec                            : Matroska
#File size                        : 2416672563
#Overall bit rate                 : 3206541
#Duration                         : 6029357
#
#Video
#Format                           : AVC
#Codec ID                         : V_MPEG4/ISO/AVC
#Codec                            : V_MPEG4/ISO/AVC
#Duration                         : 6023333
#Nominal bit rate                 : 2971000
#Width                            : 960
#Height                           : 720
#Display aspect ratio             : 1.778
#Pixel Aspect Ratio               : 1.000
#Frame rate                       : 23.976
#Scan type                        : Progressive
#
#Audio
#Format                           : AAC
#Codec ID                         : A_AAC
#Codec                            : A_AAC/MPEG4/LC
#Duration                         : 6029357
#Bit rate mode                    : VBR
#Bit rate                         : 129720
#Channel(s)                       : 6
#Sampling rate                    : 48000
#Resolution                       : 16
#Language                         : eng
#
#Text #1
#Format                           : ASS
#Codec ID                         : S_TEXT/ASS
#Codec                            : S_TEXT/ASS
#Language                         : eng

    
def set_par(dict, index, value):
    if (not dict.has_key(index)) or dict[index] is None or dict[index] == '':
        dict[index] = value

def parse_info(filename):
    """ Parses media info for filename """
    #filename = unicode(filename , "utf8")
    args = '%s -f \"%s\"'%(MEDIAINFO, filename)
    #print "parse_info",args
    #result = os.popen(args)
    #print os.system(args)

    output = subprocess.Popen(args, stdout=subprocess.PIPE).stdout
    data = output.readlines()
    output.close()

    mode = 'none'
    result = {
            'general_format' : '',
            'general_codec' : '',
            'general_size' : None,
            'general_bitrate' : None,
            'general_duration' : None,
            'video_format' : '',
            'video_codec_id' : '',
            'video_codec' : '',
            'video_bitrate' : None,
            'video_width' : None,
            'video_height' : None,
            'video_displayaspect' : None,
            'video_pixelaspect' : None,
            'video_scantype' : '',
            'audio_format' : '',
            'audio_codec_id' : '',
            'audio_codec' : '',
            'audio_bitrate' : None,
            'audio_channels' : None,
            'audio_samplerate' : None,
            'audio_resolution' : None,
            'audio_language' : '',
            }
    
    hasgetDuration = False
    for line in data:
        if not ':' in line:
            if 'General' in line:
                mode = 'General'
            elif 'Video' in line:
                mode = 'Video'
            elif 'Audio' in line:
                mode = 'Audio'
            elif 'Text' in line:
                mode = 'Text'
        else:
            key, sep, value = line.partition(':')
            key = key.strip()
            value = value.strip()
            if mode == 'General':
                if key == 'Format': set_par(result, 'general_format', value)
                if key == 'Codec': set_par(result,'general_codec', value)
                if key == 'File size': 
                    set_par(result,'general_size', value)
                if key == 'Overall bit rate': set_par(result,'general_bitrate', value)
                if key == 'Duration' and hasgetDuration == False: 
                    print "Duration=",value
                    try:
                        duration = float(value)/1000
                    except:
                        col, sep, secs = value.rpartition(' ')
                        #print col,"=",secs
                        if sep == '':
                            duration = float(value)
                        else:
                            hours, sep, minutes = col.rpartition(' ')
                            #print "hours",hours,"sep", sep, "minutes",minutes
                            if sep == '':
                                duration = int(col[0:-2])*60+int(secs[0:-1])
                                print "ok",duration
                            else:
                                duration = int(hours[0:-1])*3600+int(minutes[0:-2])*60+int(secs[0:-1])
                    set_par(result,'general_duration', duration)
                    hasgetDuration = True
            if mode == 'Video':
                if key == 'Format': set_par(result,'video_format', value)
                if key == 'Codec ID': set_par(result,'video_codec_id', value)
                if key == 'Codec': set_par(result,'video_codec', value)
                if key == 'Nominal bit rate': set_par(result,'video_bitrate', value)
                if key == 'Width': set_par(result,'video_width', value)
                if key == 'Height': set_par(result,'video_height', value)
                if key == 'Display aspect ratio': set_par(result,'video_displayaspect', value)
                if key == 'Pixel Aspect Ratio': set_par(result,'video_pixelaspect', value)
                if key == 'Scan type': set_par(result,'video_scantype', value)
            if mode == 'Audio':
                if key == 'Format': set_par(result,'audio_format', value)
                if key == 'Codec ID': set_par(result,'audio_codec_id', value)
                if key == 'Codec': set_par(result,'audio_codec', value)
                if key == 'Bit rate': set_par(result,'audio_bitrate', value)
                if key == 'Channel(s)': set_par(result,'audio_channels', value)
                if key == 'Sampling rate': set_par(result,'audio_samplerate', value)
                if key == 'Resolution': set_par(result,'audio_resolution', value)
                if key == 'Language': set_par(result,'audio_language', value)
    return result

    



if __name__ == '__main__':
    r = parse_info("D:/百度云/我的视频/高清/TheSleepyTrifecta.rmvb")
    pprint(r)
    