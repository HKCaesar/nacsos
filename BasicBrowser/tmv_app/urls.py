from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static

from tmv_app.views import index, topic_detail, term_detail, doc_detail, topic_list_detail, topic_presence_detail, stats, settings, apply_settings, topic_random, doc_random, term_random, institution_detail, author_detail, runs, apply_run_filter, delete_run, update_run, get_docs


app_name = 'tmv_app'

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^topic/(?P<topic_id>\d+)/$', topic_detail, name="topic_detail"),
    url(r'^term/(?P<term_id>\d+)/$', term_detail, name="term_detail"),
    url(r'^doc/(?P<doc_id>.+)/$', doc_detail),
    url(r'^author/(?P<author_name>.+)/$', author_detail),
    url(r'^institution/(?P<institution_name>.+)/$', institution_detail),
    url(r'^topic_list$', topic_list_detail),
    url(r'^topic_presence$', topic_presence_detail),
    url(r'^stats$', stats),
    url(r'^settings$', settings),
    url(r'^settings/apply$', apply_settings),
    url(r'^runs$', runs, name='runs'),
    url(r'^update/(?P<run_id>\d+)$', update_run, name='update'),
    url(r'^runs/apply/(?P<new_run_id>\d+)$', apply_run_filter),
    url(r'^runs/delete/(?P<new_run_id>\d+)$', delete_run),
    url(r'^topic/random$', topic_random),
    url(r'^doc/random$', doc_random),
    url(r'^term/random$', term_random),
    url(r'^get_docs$', get_docs, name="get_docs")]
    # Example:
    # (r'^BasicBrowser/', include('BasicBrowser.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),



#onyl serve static content for development
#urlpatterns += static(settings.STATIC_URL,document_root='static')

