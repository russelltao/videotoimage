# -*- coding: cp936 -*-
import PIL.Image as Image
import Image
import ImageDraw
import PIL.ImageFont as ImageFont
from makesnapshot import *
import os,sys
import mediainfo


tmpfolder = "e:/tmp/"

class CombinePhost():
    def __init__(self, targetfolder="e:/tmp/"):
        self.targetfolder=targetfolder
    
        self.baseSmallWidth = 352
        self.baseSmallHeight = 240
    
    def makeFinalPhoto(self, targetfile, videoinfo, picfiles,capturetimes):
        titleh = 70
        wnum = 4
        hnum = 4
        w = wnum*self.smallWidth
        h = hnum*self.smallHeight + titleh
        toImage = Image.new('RGB', (w, h), (255,255,255))
        dr=ImageDraw.Draw(toImage)
        
        txt1 = u'视频尺寸：%s*%s'%(videoinfo['video_width'].split(' ')[0],videoinfo['video_height'].split(' ')[0])
        t = int(videoinfo['general_duration'])
        txt2 = u'视频时长：%.2i:%.2i:%.2i'%(t/3600,(t%3600)/60,(t%3600)%60)
        txt3 = u'影片名：%s 分类：%s'%(videoinfo['filename'],videoinfo['videotype'])
        title = u"%s  %s  %s"%(txt1, txt2, txt3)
        
        tcolor = (255,255,255)
        timefont = ImageFont.truetype('simsun.ttc',36)
        titlefont = ImageFont.truetype('simsun.ttc',28)
        dr.text((5,5), title,fill=(0,0,0), font=titlefont)
        
        dr.text((10,40), u"查看全部视频请登陆至：http://lordofcarry.weebly.com/，购买请发邮件至lordofcarry@foxmail.com",fill=(184,32,5), font=ImageFont.truetype('simsun.ttc',26,index=1))
        
        i = 0
        for y in  range(hnum):
            for x in range(wnum):
                #print x,y
                fname = picfiles[i]
                #print fname
                fromImage = Image.open(fname)
                toImage.paste(fromImage,( x*self.smallWidth, titleh+y*self.smallHeight))
                dr.text(((x+1)*self.smallWidth-150, titleh+(y+1)*self.smallHeight-40), capturetimes[i],fill=tcolor, font=timefont)
                #toImage.show()
                i+=1
        
        for f in picfiles:
            os.remove(f)
        
        toImage.save(targetfile)

        
    def makeVideoAbstract(self, videofile, targetfile):
        videoinfo = mediainfo.parse_info(videofile)
        if None == videoinfo["general_duration"]:
            raise "can't get video duration"
    
        duration = float(videoinfo["general_duration"])
        if duration == 0:
            print "get duration as 0 from file "+videofile
            #logging.error("get duration as 0 from file "+videofile)
            return False
        videoinfo['filename'] = videofile.split('/')[-1]
        videoinfo['videotype'] = videofile.split('/')[-2]
        self.smallWidth = int(videoinfo['video_width'])
        self.smallHeight = int(videoinfo['video_height'])
        #print self.smallWidth,self.smallHeight
        if self.smallWidth > self.baseSmallWidth:
            
            self.smallHeight = int(self.baseSmallWidth * (float(self.smallHeight)/self.smallWidth))
            self.smallWidth = self.baseSmallWidth
            
        #print self.smallWidth,self.smallHeight
        
        fnames = []
        capturetimes = []
        s = snapshot()
        if False == s.captureVideo(videofile, self.smallWidth, self.smallHeight, duration, fnames, capturetimes):
            print "captureVideo Fail",videofile
            return False
        #print fnames
        #print videoinfo
        return self.makeFinalPhoto(targetfile, videoinfo, fnames, capturetimes)
    
if __name__ == '__main__':
    obj = CombinePhost()
    videofile = u"D:/百度云/我的视频/完整专业视频/老梦/LM-110 罪恶的医生.rmvb"
    targetfile = u"e:/new/LM-110 罪恶的医生.jpg"
    photofile = obj.makeVideoAbstract(videofile, targetfile)
    print photofile
    
