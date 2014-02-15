from django.conf.urls import patterns, include, url
from mysite.views import *
from imagemanage.views import videoshow,mynovelhtml
from django.contrib import admin
from django.views.generic import TemplateView

#from django.views.generic.list import ListView
#from imagemanage.models import TopSubject
admin.autodiscover()



urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    (r'^test/mynovel/(.*)$', mynovelhtml),
    (r'^test/howtobuy$', TemplateView.as_view(template_name='howtobuy.html')),
    (r'^test/([^/]*)(.*)$', videoshow),
    
    (r'^novel/(.*)$', novelhtml),
    (r'^(\w+)/category/(.*)$', categoryhtml),
    (r'^templates/(?P<path>.*)$', 'django.views.static.serve', 
        {'document_root': os.path.dirname(globals()["__file__"])+'/templates/'}
    ),
    url(r'^admin/', include(admin.site.urls)),
    (r'^(.*)$', indexhtml),
)