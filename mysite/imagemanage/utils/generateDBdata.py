#coding:utf-8
from imagemanage.models import TopSubject,VideoPhoto,VideoFolder
import os
import logging
import datetime

logger = logging.getLogger(__name__)


def scanAllFolders(rootfolder):
    walkitems = os.walk(rootfolder)
    
    for root, dirs, files in walkitems: 
        realroot = root[len(rootfolder)-1:]
        #realroot = realroot[realroot.rfind('/')+1:]
        for foldername in dirs: 
            pathfile = os.path.join(root, foldername)
            realpath = pathfile[len(rootfolder)-1:]
            modtime = datetime.datetime.fromtimestamp(os.stat(pathfile).st_mtime)
            thelevel = realpath.count('/')
            try:
                p = VideoFolder.objects.get(pathname=realpath)
            except VideoFolder.DoesNotExist:
                print "add new topsubject",realpath
                p = VideoFolder(pathname=realpath,name=foldername,parent=realroot,level=thelevel,modifyTime=modtime)
                p.save()
                logger.info("add to VideoFolder: name=%s,path=%s,parent=%s,level=%d,time=%s"\
                        %(foldername,realpath, realroot,thelevel,modtime)) 
            else:
                pass

                    