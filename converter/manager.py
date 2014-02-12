# -*- coding: cp936 -*-

import cominephoto
import os
import logging  





class Manage():
    def __init__(self):
        self.totalNeedProcNum = 0
        self.alreadyProcCount = 0
        self.failCount = 0
        
        self.ftypes = {}
        
    def calcFileTotalCount(self, folder):
        files = os.listdir(folder)
        
        for videofile in files:
            sourceFile = folder+videofile
            
            if os.path.isdir(sourceFile):
                self.calcFileTotalCount(sourceFile+'/')
                continue
                
            self.totalNeedProcNum+=1
            
            ext = sourceFile.rpartition('.')[2]
            if self.ftypes.has_key(ext):
                self.ftypes[ext]+=1
            else:
                self.ftypes[ext]=1

    def handlerFolder(self, folder, targetRootFolder):
        if os.path.exists(targetRootFolder) == False:
            os.mkdir(targetRootFolder)
                    
        obj = cominephoto.CombinePhost(targetRootFolder)
        files = os.listdir(folder)
        
        
        for videofile in files:
            sourceFile = folder+videofile
            
            
            if os.path.isdir(sourceFile):
                newtartgetfolder = targetRootFolder+videofile+'/'

                self.handlerFolder(sourceFile+'/', newtartgetfolder)
                continue
    
            self.alreadyProcCount+=1
            destFile = targetRootFolder+videofile+".jpg"
            if os.path.exists(destFile):
                #print "exist: "+sourceFile
                logging.debug("exist: "+sourceFile)
                continue
            
            try:
                result = obj.makeVideoAbstract(sourceFile, destFile)
            except:
                logging.error('catch exception')
                result = False
                
            if False == result:
                self.failCount+=1
                ext = sourceFile.rpartition('.')[2]
                logging.error('failed file type=[%s],name=[%s]'%(ext,sourceFile) )
                
                continue
            
            print "process %i/%i, current proc file:[%s]"%(self.alreadyProcCount,self.totalNeedProcNum,sourceFile)
            


if __name__ == '__main__':
    sourceVideoFolder = "D:/百度云/我的视频/"
    targetRootFolder = "e:/images/"
    
    logging.basicConfig(filename = targetRootFolder+"/log.txt", level = logging.INFO)
    
    m = Manage()
    m.calcFileTotalCount(sourceVideoFolder)
    print m.totalNeedProcNum
    for k,v in m.ftypes.items():
        print k,v
    m.handlerFolder(sourceVideoFolder, targetRootFolder)

    print "failed",m.failCount