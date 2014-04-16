# -*- coding: cp936 -*-

import cominephoto
import os
import logging  
from ftplib import FTP

FtpRootFolder = "/mnt/images/"
sourceVideoFolder = "D:/百度云/我的视频/"    
targetRootFolder = "e:/images/"    
newPhotoFolder = "e:/new/"   
logging.basicConfig(filename = targetRootFolder+"/log.txt", level = logging.INFO)

class Manage():
    def __init__(self):
        self.totalNeedProcNum = 0
        self.alreadyProcCount = 0
        self.failCount = 0
        
        self.ftypes = {}

    def compareVideoToPhoto(self, videoFolder, ftpFilesDict,ftpFolderDict):
        videoitems = os.walk(videoFolder)

        needProcess = []
        needDelete = []
        needDelFolder= []
        needMakeFolder= []
        hasnum = 0
        nothasnum = 0
        for root, dirs, files in videoitems: 
            for d in dirs: 
                folder = os.path.join(root, d)
                logicpath = folder[len(videoFolder):]
                ftppath = FtpRootFolder+logicpath.replace('\\','/')
                ftppath = ftppath.decode('gbk')
                if ftpFolderDict.has_key(ftppath):
                    ftpFolderDict[ftppath]=False
                else:
                    needMakeFolder.append(ftppath)
            for f in files: 
                videofile = os.path.join(root, f)
                logicpath = videofile[len(videoFolder):]
                photopath = FtpRootFolder+logicpath.replace('\\','/')+".jpg"
                
                photopath = photopath.decode('gbk')

                #print isinstance(photopath.decode('gbk'), unicode)

                if ftpFilesDict.has_key(photopath):
                    hasnum+=1
                    ftpFilesDict[photopath]=False
                    
                else:
                    nothasnum+=1
                    needProcess.append((videofile,photopath, f))
        print "compareVideoToPhoto has %d, not has %d, ftptotal=%d"%(hasnum, nothasnum, len(ftpFilesDict.items()))
        for k,v in ftpFilesDict.items():
            if v:
                needDelete.append(k)
        for k,v in ftpFolderDict.items():
            if v:
                needDelFolder.append(k)
        #for videofile,photopath, f in needProcess:
            #print "lack:",photopath
        return needProcess,needDelete,needDelFolder,needMakeFolder
    
class ftpManage():
    def __init__(self):
        self.ftp = FTP()
        self.connect()
        
        self.ftpfiles = {}
        self.ftpfolders = {}
        
    def connect(self):
        self.ftp.connect('taohui.org.cn',21,30) # 连接FTP服务器
        self.ftp.login('taohui','iamtaohui') # 登录
        print self.ftp.getwelcome()  
        self.ftp.cwd('/mnt/images')
        
    def checkFileExist(self, fpath):
        remotepath = fpath
        
        try:
            size = self.ftp.size(remotepath.encode('utf8'))
            #print "get file[%s] size %d! %s"%(remotepath,size)
            return True
        except Exception,ex:
            #print remotepath,isinstance(remotepath, unicode)
            #print "get file[%s] size Failed! %s"%(remotepath,ex)
            return False
        
    def deleteFile(self, fpath):
        remotepath = fpath
        
        try:
            self.ftp.delete(remotepath.encode('utf8'))
            #print "get file[%s] size %d! %s"%(remotepath,size)
            return True
        except Exception,ex:
            #print remotepath,isinstance(remotepath, unicode)
            print "delete file[%s] Failed! %s"%(remotepath,ex)
            return False
        
    def deleteFolder(self, fpath):
        remotepath = fpath
        
        try:
            self.ftp.rmd(remotepath.encode('utf8'))
            #print "get file[%s] size %d! %s"%(remotepath,size)
            return True
        except Exception,ex:
            #print remotepath,isinstance(remotepath, unicode)
            print "delete folder[%s] Failed! %s"%(remotepath,ex)
            return False
        
    def makeFolder(self, fpath):
        remotepath = fpath
        
        try:
            self.ftp.mkd(remotepath.encode('utf8'))
            return True
        except Exception,ex:
            print "makeFolder[%s] Failed! %s"%(remotepath,ex)
            return False
        
    def uploadFile(self, local, remote):
        try:
            return self.ftp.storbinary("STOR %s"%remote.encode('utf8','ignore'), open(local, 'rb'))
        except Exception,ex:
            print "uploadFile[%s] Failed! Exception:[%s]"%(remote,ex)
            self.quit()
            self.connect()
            return None
        
    def getAllFilename(self, folder):
        try:
            flist = self.ftp.nlst(folder)
            for i in flist:
                fname = i.decode('utf8')
                #print "folder %s has subfolder %s"%(fname, fname)
                if fname[-4:] != ".jpg":
                    self.ftpfolders[fname]=True
                    if not self.getAllFilename(fname.encode('utf8')):
                        print "Try again to show folder",fname
                        self.quit()
                        self.connect()
                        if self.getAllFilename(fname.encode('utf8')):
                            print "Try again success",fname
                        else:
                            print "Exit!"
                            exit(0)
                else:
                    self.ftpfiles[fname]=True
                    
            return True
        except Exception,ex:
            print "showFiles[%s] Failed! %s"%(folder.decode('utf8'),ex)
            return False
        
    def quit(self):
        self.ftp.quit()
        
def createIncrementPhoto():
    m = Manage()
    ftp = ftpManage()
    ftp.getAllFilename(FtpRootFolder)

    needProcess,needDelete,needDelFolder,needMakeFolder = m.compareVideoToPhoto(sourceVideoFolder, ftp.ftpfiles,ftp.ftpfolders)
    failedlistfilepath = newPhotoFolder+"faillist.txt"
    failedmap = {}
    
    for i in needMakeFolder:
        print "make folder",i
        ftp.makeFolder(i[len(FtpRootFolder):])
    
    newGenList = []
    failGenList = []
    
    if os.path.exists(failedlistfilepath):
        f = open(failedlistfilepath,'r')
        i=0
        for l in f.readlines():
            vname = l[0:-1].decode('utf8')
            #print "read",vname,len(vname)
            failedmap[vname.encode('utf8')]=True
            i+=1
        f.close()
        print "read already capture failed count:",i
    f = open(failedlistfilepath,'a+')
    obj = cominephoto.CombinePhost(targetRootFolder)
    
    totalNum = len(needProcess)
    i=0
    uploadCount=0
    uploadFailed=0
    alreadyCapFailed = 0
    capSuccess=0
    capFailed=0
    noCap=0
    for videofile,ftpfile,vname in needProcess:
        i+=1
        #print "process file:%s"%(ftpfile)
        if ftp.checkFileExist(ftpfile):
            continue

        if failedmap.has_key(videofile.decode('gbk', 'ignore').encode('utf8', 'ignore')):
            alreadyCapFailed+=1
            continue
        else:
            print "%d/%d"%(i,totalNum),vname

        cap = False
        newfile = newPhotoFolder+vname+".jpg"
        
        if os.path.exists(newfile):
            cap = True
            noCap+=1
        else:
            try:
                cap = obj.makeVideoAbstract(videofile, newfile)
                if cap:
                    capSuccess+=1
            except Exception, ex:
                logging.error('catch exception: %s'%(ex))
        
        if cap:
            
            newGenList.append(vname)
            print "ready to upload file",newfile,isinstance( ftpfile[len(FtpRootFolder):], unicode)
            if None == ftp.uploadFile(newfile, ftpfile[len(FtpRootFolder):]):
                print "upload file failed!"
                uploadFailed+=1
            else:
                print "upload file success!",ftpfile
                uploadCount+=1
        else:
            capFailed+=1
            f.write(videofile.decode('gbk', 'ignore').encode('utf8')+'\n')
            failGenList.append(vname)
            f.flush()
            

    f.close()
    
    print "capture success:%d.failed:%d.alreadyCapFailed=%d"%(capSuccess,capFailed,alreadyCapFailed)
    print "uploadcount success:%d,fail:%d. "%(uploadCount,uploadFailed)
    for i in needDelete:
        print "delete",i
        ftp.deleteFile(i[len(FtpRootFolder):])
        
    for i in needDelFolder:
        print "delete folder",i
        ftp.deleteFolder(i[len(FtpRootFolder):])
    ftp.quit()

if __name__ == '__main__':
    createIncrementPhoto()

    
