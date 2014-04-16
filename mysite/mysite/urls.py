from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns  
from imagemanage.views import scanfolder,OnlineUserPageView,VideoPageView,PicDetailPageView,NovelPageView,OnlineWatchPageView
from django.contrib import admin
from django.views.generic import TemplateView
import os
from userena import views as userena_views
from django.views.decorators.cache import cache_page
from sitemap import PostSitemap
from django.contrib.sitemaps import views as sitemap_views

admin.autodiscover()



urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    #url(r'^accounts/signup/$', userena_views.signup, {'signup_form': "userena/signup_form.html"}, name='userena_signup'),
    (r'^accounts/', include('userena.urls')),
    (r'^mynovel/(?P<novelname>.*)$', NovelPageView.as_view()),
    (r'^picdetail/(?P<picname>.*)$', PicDetailPageView.as_view()),
    (r'^howtobuy$', TemplateView.as_view(template_name='howtobuy.html')),
    (r'^onlineuser$', OnlineUserPageView.as_view()),
    (r'^scanfolder$', scanfolder),
    (r'^online$', OnlineWatchPageView.as_view()),
    
    url(r'^sitemap\.xml$', cache_page(60 * 60 * 12)(sitemap_views.sitemap), {'sitemaps': {'posts': PostSitemap}}),
    
    (r'^templates/(?P<path>.*)$', 'django.views.static.serve', 
        {'document_root': os.path.dirname(globals()["__file__"])+'/templates/'}
    ),
    url(r'^admin/', include(admin.site.urls)),
    (r'^i18n/', include('django.conf.urls.i18n')),
    (r'^(?P<category>[^/]*)(?P<subtype>.*)$', VideoPageView.as_view()),
)

urlpatterns += staticfiles_urlpatterns() 

