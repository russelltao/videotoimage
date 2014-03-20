#coding:utf-8

from django.contrib.sitemaps import Sitemap
from imagemanage.views import Cacheinfo
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
            logger.debug("%s,%s,"%(p.pathname,p.modifyTime))
        return siteurl

    def lastmod(self, obj):
        return obj[1]

    def location(self, obj):
        return obj[0]
