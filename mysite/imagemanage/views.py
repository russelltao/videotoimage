#coding:utf-8
from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse
import os, time, datetime
from models import TopSubject,VideoFolder,OnlineWatchVideo
from types import *
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _
from utils.cache import cache as memcache
from utils.generateDBdata import scanAllFolders
from utils.getiploc import iplocater,string2ip
import logging
from django.views.generic.base import TemplateView
from django.views.generic import ListView


thumbnailPrefix = "/resize/"
initialPicPrefix = "/image/"
detailPicPrefix = "/picdetail/"
novelFolder = "/home/novel/"
resizeImageFolder = "/static/resize/"
bigImageFolder = "/static/image/"
DiskRootFolder = '/mnt/images/'

logger = logging.getLogger(__name__)

def scanfolder(request):
    scanAllFolders(DiskRootFolder)
    return HttpResponse('<h1>success</h1>')

class Cacheinfo():
    def __init__(self):
        self.files = []
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
            if f != "HotAsionKo" and f != "月空":
                l.append("<a href=\"/%s/%s\">%s<small>[%d]</small></a>"%(realpath[len(DiskRootFolder):], f,f,filecount))
            t = self.walkAddFolder(subrealfolder)
            if t:
                l.append(t)

        return l
        
    def checkTopSubject(self):
        
        self.topsubjects = {}
        #print "checkTopSubject running..."
        topfolder = os.listdir(DiskRootFolder)
        for tf in topfolder:
            realpath = os.path.join(DiskRootFolder, tf)

            if os.path.isdir(realpath):
                try:
                    p = TopSubject.objects.get(name=tf)
                except TopSubject.DoesNotExist:
                    print "add new topsubject",tf
                    p = TopSubject(name=tf,path=realpath,price=5,descinfo='[%s]类每个视频价格为5元'%(tf))
                    p.save()
                else:
                    pass
                    
                self.tmpFileCount=0
                treelist = self.walkAddFolder(realpath)

                #if len(treelist) > 0:
                    #print "tt",treelist
                walkitems = os.walk(realpath)
                self.topsubjects[tf] = [p.price, walkitems, treelist, self.tmpFileCount,p.descinfo, p.keywords]
                

    def walkAll(self): 
        self.files = memcache.get("files")
        if self.files == None:
            print "cache none files"
        else:
            print "cache meet files"
            return
            
        self.files = []
        
        walkitems = os.walk(DiskRootFolder)
        
        for root, dirs, files in walkitems: 
            for f in files: 
                if f[-3:] != "jpg":
                        #print os.path.join(root, f)
                    continue
                pathfile = os.path.join(root, f)

                self.files.append((pathfile, os.stat(pathfile).st_mtime, detailPicPrefix+pathfile[len(DiskRootFolder):]))
                        
        self.files.sort(key = lambda l: (l[1], l[0]), reverse = True)
        
        memcache.set("files",self.files, 300)


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



class BaseMixin(object):

    def get_context_data(self, *args, **kwargs):
        context = super(BaseMixin, self).get_context_data(**kwargs)
        try:
            context['online_num'] = len(memcache.get('online_ips'))
        except Exception as e:
            logger.exception(u'加载基本信息出错[%s]！', e)

        return context

class OnlineUserPageView(BaseMixin, TemplateView):
    template_name = "onlineuser.html"

    def get_context_data(self, **kwargs):
        context = super(OnlineUserPageView, self).get_context_data(**kwargs)
        onlineips = memcache.get('online_ips')
        onlineusers = []
        for ip in onlineips:
            address = iplocater.getIpAddr( string2ip( ip ) )
            if '阿里云' in address or '淘宝' in address or '谷歌' in address:
                continue
    
            onlineusers.append((ip,address))
        context['onlineusers'] = onlineusers
        return context

class VideoPageView(BaseMixin, ListView):
    template_name = "videoshow.html"
    paginate_by = 5  # 每页显示的记录数
    cache = Cacheinfo()
    category = ""
    subtype = ""
    isShowLatestVideo = False
    
    searchResultNum = 0
    isSearch = False
    maxSearchNum = 20
    
    
    categoryValid = True
    completetype = ""
    
    latestShowNum = 49 # 最新视频显示总数
    topfilenum = 0 # 分类里最高目录的文件数
    
    def __init__(self):
        self.cache.checkTopSubject()
        self.cache.walkAll()
    
    def parse_url(self, kwargs):
        self.category = kwargs.get("category",None)
        self.subtype = kwargs.get("subtype",None)
        if self.category == "latestvideo":
            self.isShowLatestVideo = True
        else:
            self.category = self.category.encode('utf-8')
            
        self.completetype = self.category
        if self.subtype != '':
            self.completetype = self.category+self.subtype.encode('utf-8')
            
        if not self.cache.topsubjects.has_key(self.category):
            self.category = self.cache.topsubjects.items()[-1][0]
            self.isShowLatestVideo = True
            self.categoryValid = False
            
    def get_queryset(self):
        logger.debug("get_queryset page:%s"%(self.kwargs.get("page",None)))
        
        self.parse_url(self.kwargs)
        tmplist = []
        
        self.query = self.request.GET.get('s')
        if self.query:
            self.isSearch = True
            logger.debug("s:%s"%(self.query))
            self.searchResultNum = 0
            for fnames in self.cache.files:
                name = fnames[0][fnames[0].rfind('/')+1:]
                if self.query.encode('utf-8').lower() in name.lower():
                    logger.debug("find:%s in %s"%(self.query,name.decode('utf-8')))
                    self.searchResultNum+=1
                    if self.searchResultNum < self.maxSearchNum:
                        sitepath = fnames[0][len(DiskRootFolder):]
                        imgsrc = resizeImageFolder+sitepath
                        bigimgsrc = detailPicPrefix+sitepath
                        tmppathname = sitepath[0:-4]
                        alt = tmppathname[0:tmppathname.rfind('.')].replace('/',' ')
                        tmplist.append((imgsrc,tmppathname, bigimgsrc, alt))
                    

            self.paginate_by = self.maxSearchNum
            return tmplist

        find = False
        
        n=0
        if self.categoryValid:
            for root, dirs, files in self.cache.topsubjects[self.category][1]:
                if n == 0:
                    #print "root",root
                    self.topfilenum = len(files)
                n+=1
                curname = root[len(DiskRootFolder):]
        
                if curname == self.completetype:       
                    for f in files:
                        wholepath = os.path.join(root, f)
                        sitepath = wholepath[len(DiskRootFolder):]
                        imgsrc = resizeImageFolder+sitepath
                        bigimgsrc = detailPicPrefix+sitepath
                        tmppathname = sitepath[0:-4]
                        alt = tmppathname[0:tmppathname.rfind('.')].replace('/',' ')
                        tmplist.append((imgsrc,tmppathname, bigimgsrc, alt))
                    
                    find = True
                    break
        
            if not find:
                logger.error('not find %s'%('/'+self.completetype))
            else:
                return tmplist
        
        if self.isShowLatestVideo:
            #print "taohui"
            i = 0
            for f in self.cache.files:
                i += 1
                sitepath = f[0][len(DiskRootFolder):]
                imgsrc = resizeImageFolder+sitepath
                bigimgsrc = detailPicPrefix+sitepath
                tmppathname = sitepath[0:-4]
                alt = tmppathname[0:tmppathname.rfind('.')].replace('/',' ')
                tmplist.append((imgsrc,tmppathname, bigimgsrc, alt))
                if i > self.latestShowNum:
                    break
    
        return tmplist

    def genFolderTree(self, context):
        treelist = "<a href=\"/%s\">%s<small>[%d]</small></a>"\
        %(self.category, self.category, self.topfilenum),self.cache.topsubjects[self.category][2]
        context["treelist"]=unordered_list(treelist)
        
    def genTopCategeryList(self, context):
        names = []
        
        for k,v in self.cache.topsubjects.items():
            if k == self.category and not self.isShowLatestVideo:
                names.append(("%s[%d]"%(k,v[3]), '/'+k, True))
            else:
                names.append(("%s[%d]"%(k,v[3]), '/'+k, False))

        context["topsubjectnames"]=names
        
    def genShowInfo(self, context):
        showinfo = "以下视频是站长最新上传的%d部视频。每个截图上方有视频分辨华和截图!"%(self.latestShowNum)
        if self.isSearch:
            showinfo = "查询关键字[%s]共搜索到%d结果!"%(self.query.encode('utf-8'), self.searchResultNum)
            if self.searchResultNum>self.maxSearchNum:
                showinfo += "但最多仅显示前%d个结果！请使用更详细的词进行搜索"%(self.maxSearchNum)
        elif not self.isShowLatestVideo:
            showinfo = "[%s]类:  %s"%(self.category,self.cache.topsubjects[self.category][4].encode('utf8'))
    
        context["price"] = showinfo
        
    def get_context_data(self, **kwargs):
        logger.debug("get_context_data page:%s"%(self.kwargs.get("page",None)))
        context = super(VideoPageView, self).get_context_data(**kwargs)

        if self.isShowLatestVideo:
            context["videocategory"] = "最新视频|"
    
        if self.categoryValid:
            context["videocategory"] = self.category+"|"
    
        self.genTopCategeryList(context)
        self.genShowInfo(context)
        self.genFolderTree(context)
        
        
        if not self.isShowLatestVideo and self.completetype != "" and self.completetype != "/":
            logger.info("completetype=%s"%(self.completetype))
            try:
                p = VideoFolder.objects.get(pathname='/'+self.completetype)
                logger.debug("parent=%s,keywords=%s"%(p.parent,p.keywords))
                context['keywords'] = p.keywords
                context['subtypedesc'] = p.descinfo
                context['subname'] = '[%s]'%(p.name)
            except VideoFolder.DoesNotExist:
                context['keywords'] = self.cache.topsubjects[self.category][5].encode('utf8')
                logger.error('not find %s in VideoFolder'%('/'+self.completetype))
        
        return context

class PicDetailPageView(BaseMixin, TemplateView):
    template_name = "picdetail.html"

    def get_context_data(self, **kwargs):
        context = super(PicDetailPageView, self).get_context_data(**kwargs)
        name = kwargs.get("picname",None)
        logger.debug("picname:%s"%(name))
        videoname = name[0:name.rfind(".")]
        videoname = videoname[0:videoname.rfind(".")]
    
        context["picinfo"]=name
        context["bigimgsrc"]=bigImageFolder+name
        context['videoname'] = videoname[videoname.rfind("/")+1:]
        context['keywords'] = videoname.replace('/',',')
        return context
    
baiduOnlineFiles = [\
                    "http://bcs.duapp.com/myvideoshare/media/110%E6%96%A4--IlScatenato%E6%AD%BB%E6%B2%89%E6%AD%BB%E6%B2%89_MP4_AVC_AAC_320x240_20140303164311.mp4"\
                    ,]
class OnlineWatchPageView(BaseMixin, TemplateView):
    template_name = "onlinevideo.html"

    def get_context_data(self, **kwargs):
        context = super(OnlineWatchPageView, self).get_context_data(**kwargs)
        
        watchs = OnlineWatchVideo.objects.all()
        
        weekday = datetime.date.today().isoweekday()
        
        t = weekday%len(watchs)
        logger.info("weekday:%d,%d"%(weekday,t))

        context["videofileurl"]=watchs[t].url
        context["desc"]=watchs[t].desc
        context["videoname"]=watchs[t].name
        context['keywords'] = watchs[t].keywords
        return context
    
class novelmanage():
    def __init__(self):
        self.folder = novelFolder
        self.filelist = []
        
    def readFolder(self):
        self.filelist = os.listdir(self.folder)
        self.filelist.sort(self.compare)
        return self.filelist
    
    def getNovelSitemap(self):
        nlist = self.readFolder()
        slist = []
        for f in nlist:
            loc = "/mynovel/"+f.decode('utf-8')
            t = datetime.datetime.fromtimestamp(os.stat(self.folder + "/" + f).st_ctime)
            slist.append((loc, t))
        return slist
        
    def read(self, name):
        f = open(name, 'r')
        fcontent = f.read()
        f.close()
        return fcontent

    def compare(self, x, y):
        stat_x = os.stat(self.folder + "/" + x)
        stat_y = os.stat(self.folder + "/" + y)
        if stat_x.st_ctime < stat_y.st_ctime:
            return -1
        elif stat_x.st_ctime > stat_y.st_ctime:
            return 1
        else:
            return 0
        
class NovelPageView(BaseMixin, TemplateView):
    template_name = "mynovel.html"

    def get_context_data(self, **kwargs):
        context = super(NovelPageView, self).get_context_data(**kwargs)
        name = kwargs.get("novelname",None)
        
        novel = novelmanage()
        nlist = novel.readFolder()
    
        if name == "main":
            name = nlist[0]
        else:
            name = name.encode('utf-8')
            
        filename = os.path.join(novelFolder, name)
        
        f = open(filename, 'r')
        fcontent = f.read()
        f.close()

        context["names"]=nlist
        context["novelname"]=name
        context['content'] = fcontent.decode('gbk', 'ignore').encode('utf-8')

        return context


if __name__ == "__main__":
    print "ok"
    