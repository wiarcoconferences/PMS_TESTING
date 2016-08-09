from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'myintervals.views.home', name='home'),
    
    url(r'^documents/(?P<task>(:?add|:?edit|:?active|:?delete))/$', 'documents.views.documents_details', name='documnets_details'),
    url(r'^add/documents/$', 'documents.views.add_document', name='add_document'),
    url(r'^documents-home/$', 'documents.views.documents_home', name='documents_home'),
    url(r'^my-documents/$', 'documents.views.my_documents', name='my_documents'),
    url(r'^ajaxmilestonetasks/', 'documents.views.get_milestone_tasks', name='ajax-milestone-tasks'),
    url(r'^getajaxtasks/', 'documents.views.get_ajax_tasks', name='get-ajax-tasks'),
    url(r'^tags/', 'documents.views.tags_list', name='tags_list'),
)
