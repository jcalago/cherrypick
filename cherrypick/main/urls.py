from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import direct_to_template
from cherrypick.main.views import InboxView, TodayView, APIView

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('cherrypick.main.views',
    # Examples:
     url('^test/', 'test'),
     url(r'^update_item/$', 'update_item', name='main__update_item'),
     #url(r'^inbox/(?P<inbox>[^/]*)/$', 'inbox', name='main__inbox'),
     url(r'^inbox/(?P<inbox>[^/]*)/$', InboxView.as_view(), name='main__inbox'),
     url(r'^api/(?P<cmd>\w+)/$', APIView.as_view(), name='main__api'),
     #url(r'^', 'today', name='main__today'),
     url(r'^', TodayView.as_view(), name='main__today'),
     #(r'^inbox/(?P<inbox>.*)/?$', direct_to_template, {'template': 'main/inbox.html'}),
     
    # url(r'^$', 'cherrypick.views.home', name='home'),
    # url(r'^cherrypick/', include('cherrypick.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
