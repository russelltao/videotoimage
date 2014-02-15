# -*- coding: utf-8 -*- 

from django.http import HttpResponse
import time
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse
import csv
import os
#import sae.storage

#rootpicfolder='/home/tmp/videophoto/'
thumbnailPrefix = "/resize/"
initialPicPrefix = "/image/"
categoryhtmlPrefix = "/category/"

rootResourceFolder = '/home/myresource/'

novelFolder = "/home/novel/"

class Cacheinfo():
    def __init__(self, type, foldername):
        self.isInit = False
        
        self.files = []
        self.maxFileInPage = 400
        self.allfile = {}
        self.lastInitTime = 0
        self.type = type
        self.foldername = foldername
        self.rootFolder = rootResourceFolder+foldername+"/"

    def readall(self):
        self.files = []
        self.allfile = {}
        
        topfolders = os.listdir(self.rootFolder)

        for c in topfolders:
            realpath = os.path.join(self.rootFolder, c)
            #print c, os.path.isdir(realpath)
            if not os.path.isdir(realpath):
                continue
            self.allfile[c] = []
            #print "realpath",realpath
            list_dirs = os.walk(realpath) 
        
            for root, dirs, files in list_dirs: 
                #for d in dirs: 
                    #pass
                    #self.folders.append( os.path.join(root, d) )     
                for f in files: 
                    if f[-3:] != "jpg":
                        print os.path.join(root, f)
                        continue
                    pathfile = os.path.join(root, f)
                    self.allfile[c].append( pathfile )

                    self.files.append((pathfile, os.stat(pathfile).st_mtime))

        #self.topfolders = os.listdir(rootpicfolder)
        self.files.sort(key = lambda l: (l[1], l[0]), reverse = True)
        #print self.files
        print "do read all, total category:",len(self.allfile)
        self.isInit = True
        self.lastInitTime = time.time()
        
    def checkNeedInit(self):
        detra = time.time() - self.lastInitTime
        #print "cache time detra:",detra
        if self.isInit == False or detra > 600:
            self.readall()
        
    def renderFiles(self, thefiles, topN):
        files = []
        i = 0
        lineflag = True
        for f in thefiles:
            i+=1
            if i > topN:
                break
            truefile = f[len(rootResourceFolder):]
            if i % 2 != 0:
                lineflag = True
            else:
                lineflag = False
            files.append((thumbnailPrefix+truefile, initialPicPrefix+truefile, lineflag))
            #print thumbnailPrefix+truefile
        return files
    
    def getTopFiles(self, topN):
        self.checkNeedInit()
            
        t = []
        i = 0
        print "total files:",len(self.files)
        for a in self.files:
            i+=1
            if i > topN:
                break
            #print a[0]

            t.append(a[0])
        return self.renderFiles(t, topN)
    
    def getTopfolders(self):
        self.checkNeedInit()
            
        tfolders = []
        i=0
        for k,v in self.allfile.items():
            i+=1
#             print i,k
            tfolders.append(("%d-%s[%d部]"%(i,k,len(v)), "/"+self.type+categoryhtmlPrefix+k))

        return tfolders
    
    def getFolderFile(self,folder):
        self.checkNeedInit()
        
        if self.allfile.has_key(folder):
            return self.renderFiles(self.allfile[folder], self.maxFileInPage)
        else:
            print "search error:",folder,self.allfile.items()

            return None


uriFolder = {
             "video":("videophoto", Cacheinfo("video","videophoto"),"5元专业视频相册"),
             "zhongyi":("zhongyi", Cacheinfo("zhongyi","zhongyi"),"2元综艺横抱相册"),
             "movie":("movieclips", Cacheinfo("movie","movieclips"),"2元昏迷公主抱相册")
             }

def renderFrame(cinfo, type):
    topfolders = cinfo.getTopfolders()
    typelist = []
    for k,v in uriFolder.items():
        color = "blue"
        active = False
        fs = 80
        if k == type:
            color = "red"
            fs = 120
            active = True
        typelist.append(("/"+k, v[2], color, fs, active))
    d = {
         "topfolders":topfolders, 
         "category":"最新20部视频", 
         "cateCount":len(topfolders),
         "typelist":typelist
         }
    return d
    
def indexhtml(request, type):
    manager = uriFolder["video"][1]
    if uriFolder.has_key(type):
        manager = uriFolder[type][1]
    else:
        type = "video"
    t = get_template('index.html')
    topfiles = manager.getTopFiles(20)
    
    d = renderFrame(manager, type)
    d["topfiles"]=topfiles

    c = Context( d )
    html = t.render(c)
    return HttpResponse(html)


def categoryhtml(request,type, category):
    category = category.encode('utf-8')
    print "category",category
    
    manager = uriFolder["video"][1]
    if uriFolder.has_key(type):
        manager = uriFolder[type][1]
    else:
        type = "video"
        
    t = get_template('index.html')
    topfiles = manager.getFolderFile(category)

    if topfiles == None:
        return HttpResponse("Error Category!")

    d = renderFrame(manager, type)
    d["topfiles"]=topfiles
    d["category"]="["+category+"],video number:"+str(len(topfiles))
    c = Context( d )
    html = t.render(c)
    return HttpResponse(html)



    
class novelmanage():
    def compare(self, x, y):
        stat_x = os.stat(self.folder + "/" + x)
        stat_y = os.stat(self.folder + "/" + y)
        if stat_x.st_ctime < stat_y.st_ctime:
            return -1
        elif stat_x.st_ctime > stat_y.st_ctime:
            return 1
        else:
            return 0
    def __init__(self):
        self.folder = novelFolder
        self.filelist = []
        
    def readFolder(self):
        self.filelist = os.listdir(self.folder)
        self.filelist.sort(self.compare)
        return self.filelist
        
    def read(self, name):
        f = open(name, 'r')
        fcontent = f.read()
        f.close()
        return fcontent
    
def novelhtml(request, name):
    novel = novelmanage()
    nlist = novel.readFolder()
    if name == "main":
        name = nlist[0]
    else:
        name = name.encode('utf-8')
    
    filename = os.path.join(novelFolder, name)
    print "novel",name,"realname",filename
    
    
    f = open(filename, 'r')
    fcontent = f.read()
    f.close()
    print len(fcontent)#, fcontent.decode('gbk').encode('utf-8') 
    
    t = get_template('novel.html')
    d = {"names":nlist,"cateCount":len(nlist),"content":fcontent.decode('gbk').encode('utf-8')}
    c = Context( d )
    html = t.render(c)
    return HttpResponse(html)



if __name__ == "__main__":
    print "ok"
    