#coding:utf-8

from django.contrib.sitemaps import Sitemap
from imagemanage.views import Cacheinfo, novelmanage
from imagemanage.models import VideoFolder
import datetime
import logging


logger = logging.getLogger(__name__)


class PostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.2

    def items(self):
        cache = Cacheinfo()
        cache.walkAll()
        siteurl = []

        for f in cache.files:
            siteurl.append((f[2].decode('utf-8'),datetime.datetime.fromtimestamp(f[1])))
            
        for p in VideoFolder.objects.all():
            siteurl.append((p.pathname,p.modifyTime))
            logger.debug("sitemap for folder: %s,%s,"%(p.pathname,p.modifyTime))

        novel = novelmanage()
        nlist = novel.getNovelSitemap()
        for f in nlist:
            siteurl.append(f)
            logger.debug("sitemap for novel: %s,%s,"%(f[0],f[1]))
        
        return siteurl

    def lastmod(self, obj):
        return obj[1]

    def location(self, obj):
        return obj[0]
