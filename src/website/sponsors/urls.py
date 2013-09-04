from django.conf.urls.defaults import patterns

urlpatterns = patterns('website.sponsors.views',
    (r'^$', 'index'),
    (r'^call_cbui$', 'call_cbui'),
    (r'^thanks$', 'thanks'),
    (r'^register$', 'register_recipient'),
    (r'^thanks_recipient$', 'thanks_recipient'),
)
