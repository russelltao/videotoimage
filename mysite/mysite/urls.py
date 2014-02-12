from django.conf.urls import patterns, include, url
from mysite.views import *
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    (r'^test/(.*)$', test),
    (r'^novel/(.*)$', novelhtml),
    (r'^(\w+)/category/(.*)$', categoryhtml),
    (r'^templates/(?P<path>.*)$', 'django.views.static.serve', 
        {'document_root': os.path.dirname(globals()["__file__"])+'/templates/'}
    ),
    url(r'^admin/', include(admin.site.urls)),
    (r'^(.*)$', indexhtml),
)