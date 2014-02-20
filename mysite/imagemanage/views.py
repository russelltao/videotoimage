#coding:utf-8
from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse
import os
import time
from models import TopSubject
from types import *
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.shortcuts import render_to_response


#rootpicfolder='/home/tmp/videophoto/'
thumbnailPrefix = "/resize/"
initialPicPrefix = "/image/"

novelFolder = "/home/novel/"

resizeImageFolder = "/static/resize/"
bigImageFolder = "/static/image/"

DiskRootFolder = '/mnt/images/'


class Cacheinfo():
    def __init__(self):
        self.isInit = False
        
        self.files = []
        self.lastInitTime = 0
        
        self.topsubjects = {}
        
        self.tmpFileCount = 0
        
    def walkAddFolder(self, realpath):
        l = []

        folders = os.listdir(realpath)
        
        for f in folders:
            subrealfolder = os.path.join(realpath, f)
            if not os.path.isdir(subrealfolder):
                self.tmpFileCount+=1
                continue
            
            items = os.listdir(subrealfolder)
            filecount = 0
            for calcf in items:
                tmp = os.path.join(subrealfolder, calcf)
                if not os.path.isdir(tmp):
                    filecount+=1
            l.append("<a href=\"/%s/%s\">%s<small>[%d]</small></a>"%(realpath[len(DiskRootFolder):], f,f,filecount))
            t = self.walkAddFolder(subrealfolder)
            if t:
                l.append(t)

        return l
        
    def checkTopSubject(self):
        self.topsubjects = {}
        self.files = []
        print "checkTopSubject running..."
        topfolder = os.listdir(DiskRootFolder)
        for tf in topfolder:
            realpath = os.path.join(DiskRootFolder, tf)

            if os.path.isdir(realpath):
                try:
                    p = TopSubject.objects.get(name=tf)
                except TopSubject.DoesNotExist:
                    print "add new topsubject",tf
                    p = TopSubject(name=tf,path=realpath,price=5)
                    p.save()
                else:
                    pass
                    
                self.tmpFileCount=0
                treelist = self.walkAddFolder(realpath)
                #print tf,self.tmpFileCount
                #if len(treelist) > 0:
                    #print "tt",treelist
                walkitems = os.walk(realpath)
                self.topsubjects[tf] = (p.price, walkitems, treelist, self.tmpFileCount )
                
        walkitems = os.walk(DiskRootFolder)
        
        for root, dirs, files in walkitems: 
            for f in files: 
                if f[-3:] != "jpg":
                        #print os.path.join(root, f)
                    continue
                pathfile = os.path.join(root, f)

                self.files.append((pathfile, os.stat(pathfile).st_mtime))
                        
        self.files.sort(key = lambda l: (l[1], l[0]), reverse = True)
                
        self.isInit = True
        self.lastInitTime = time.time()

        
    def checkNeedInit(self):
        detra = time.time() - self.lastInitTime
        #print "cache time detra:",detra
        if self.isInit == False or detra > 600:
            print "update cache!"
            self.checkTopSubject()


def unordered_list(value): 
    def _recurse_children(parent): 
        temp = '' 

        for child in parent: 
            if type(child) == ListType: 
                temp += '<ul>' + _recurse_children(child) + '</ul>' 
            else: 
                if temp != '': 
                    temp += '</li>' 

                temp += '<li>' + child

        return temp 

    return _recurse_children(value) 

cache = Cacheinfo()
#cache.checkTopSubject()

def videoshow(request, category, subtype):
    cache.checkTopSubject()
    
    isShowLatestVideo = False
    if category == "latestvideo":
        isShowLatestVideo = True
        print "ok"
    #print "category",category,"subtype",subtype
    category = category.encode('utf-8')
    
    completetype = category
    if subtype != '':
        completetype = category+subtype.encode('utf-8')

    
    
    if not cache.topsubjects.has_key(category):
        #print type(category),type(cache.topsubjects.items()[0][0])
        category = cache.topsubjects.items()[-1][0]
        isShowLatestVideo = True

    t = get_template('home.html')

    d = {}
    
    names = []
    
    for k,v in cache.topsubjects.items():
        if k == category and not isShowLatestVideo:
            names.append(("%s[%d]"%(k,v[3]), '/'+k, True))
        else:
            names.append(("%s[%d]"%(k,v[3]), '/'+k, False))
        
        
    d["topsubjectnames"]=names
    find = False
    tmplist = []
    n=0
    topfilenum = 0
    for root, dirs, files in cache.topsubjects[category][1]:
        if n == 0:
            print "root",root
            topfilenum = len(files)
        n+=1
        curname = root[len(DiskRootFolder):]

        if curname == completetype:
            print "find",completetype, dirs,files
            
            for f in files:
                wholepath = os.path.join(root, f)
                sitepath = wholepath[len(DiskRootFolder):]
                imgsrc = resizeImageFolder+sitepath
                bigimgsrc = bigImageFolder+sitepath
                tmplist.append((imgsrc,sitepath[0:-4], bigimgsrc))
            
            find = True
            break

    if not find:
        print "not find", completetype
        
    latestNum = 20
    if isShowLatestVideo:
        print "taohui"
        i = 0
        for f in cache.files:
            i += 1
            sitepath = f[0][len(DiskRootFolder):]
            print "sitepath",sitepath,type(resizeImageFolder),type(sitepath)
            imgsrc = resizeImageFolder+sitepath
            bigimgsrc = bigImageFolder+sitepath
            tmplist.append((imgsrc,sitepath[0:-4], bigimgsrc))
            if i > latestNum:
                break
            
    limit = 5  # 每页显示的记录数

    paginator = Paginator(tmplist, limit)  # 实例化一个分页对象

    page = request.GET.get('page')  # 获取页码
    try:
        tmplist = paginator.page(page)  # 获取某页对应的记录
    except PageNotAnInteger:  # 如果页码不是个整数
        tmplist = paginator.page(1)  # 取第一页的记录
    except EmptyPage:  # 如果页码太大，没有相应的记录
        tmplist = paginator.page(paginator.num_pages)  # 取最后一页的记录

    d["showimages"] = tmplist
    showinfo = "以下视频是站长最新上传的20部视频。每个截图上方有视频分辨华和截图，请大家看清楚需要再购买。"
    if not isShowLatestVideo:
        showinfo = "[%s]类每个视频价格为%d元"%(category,cache.topsubjects[category][0])
    d["price"] = showinfo
    
    treelist = "<a href=\"/%s\">%s<small>[%d]</small></a>"%(category, category, topfilenum),cache.topsubjects[category][2]

    d["treelist"]=unordered_list(treelist)
    #print "treelist",treelist
    

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
    
def mynovelhtml(request, name):
    novel = novelmanage()
    nlist = novel.readFolder()
    print nlist
    if name == "main":
        name = nlist[0]
    else:
        name = name.encode('utf-8')
    
    filename = os.path.join(novelFolder, name)
    print "mynovel",name,"realname",filename
    
    
    f = open(filename, 'r')
    fcontent = f.read()
    f.close()
    print len(fcontent)
    
    t = get_template('mynovel.html')
    d = {"names":nlist,"novelname":name,"content":fcontent.decode('gbk').encode('utf-8')}
    c = Context( d )
    html = t.render(c)
    return render_to_response('mynovel.html',d)



if __name__ == "__main__":
    print "ok"
    