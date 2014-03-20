# -*- coding: utf-8 -*- 
import urllib2

urlPrefix="https://pcs.baidu.com/rest/2.0/pcs/"

pathPrefix="path=/apps/videoshare/"

token="23.bc917bfdc6d4c22aaf3bd10732b0ef01.2592000.1396421707.3674485908-2269615"
access_token="access_token="+token


def getStorageInfo():
    req = urllib2.Request("%squota?%s&method=info"%(urlPrefix,access_token))
    response = urllib2.urlopen(req)
    the_page = response.read()
    
    print the_page
    
def getFolderInfo(foldername):
    url = "%sfile?%s&method=list&%s%s"%(urlPrefix,access_token,pathPrefix,foldername)
    print url
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    the_page = response.read()
    
    print the_page
    
def sharePrivateFile(filepath):
    url = "%sfile?%s&method=list&%s%s"%(urlPrefix,access_token,pathPrefix,filepath)
    print url
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    the_page = response.read()
    
    print the_page
    
if __name__ == '__main__':
    getFolderInfo('我的视频')