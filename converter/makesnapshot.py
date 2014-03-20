# -*- coding: cp936 -*-
import subprocess
import os,sys,locale
from ctypes import * 
import mediainfo

runffmpeg=u"ffmpeg -ss %s -i \"%s\" -y -f image2 -loglevel panic -t 0.001 -s %ix%i \"%s\""



class snapshot():
    def __init__(self, photonumber = 16, targetfolder="e:/tmp/"):
        self.targetfolder = targetfolder
        self.photonumber = photonumber

    def createSnapshot(self, filename, t, photofilename):
        args = runffmpeg%(t, filename,  self.w, self.h, photofilename)
        
        #print args
        os.system(args)
        
        if os.path.exists(photofilename) == False:
            print "create photo failed",args
            return False
        
        return True
        #output = subprocess.Popen(args, stdout=subprocess.PIPE).stdout
        #data = output.readlines()
        #output.close()
        
    def captureVideo(self, videofile, w, h, duration, jpgfiles=[], capturetimes=[]):
        #print videofile
        interval = float("%.3f"%(duration/(self.photonumber+2)))
        t = interval
        #print interval
        
        self.w = w
        self.h = h
    
        
        for i in range(self.photonumber):
            t+=interval
            fname = "%soutput_%s.jpg"%(self.targetfolder,t)
            
            showtime = "%.2i:%.2i:%.2i"%(t/3600,(t%3600)/60,(t%3600)%60)

            capturetimes.append(showtime)
        
            if self.createSnapshot(videofile,t,fname) == False:
                return False
            jpgfiles.append(fname)
            
        return True
        
if __name__ == '__main__':
    videofile = u"E:/wh/捂晕 28 千金绑架案（流畅）.rmvb"
    
    videoinfo = mediainfo.parse_info(videofile)
    if None == videoinfo["general_duration"]:
        raise "can't get video duration"

    duration = float(videoinfo["general_duration"])
        
    s = snapshot()
    jpgfiles=[]
    capturetimes=[]
    videoinfo = s.captureVideo(videofile, duration, jpgfiles, capturetimes)


