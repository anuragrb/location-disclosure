from django.conf.urls import patterns, include, url

from django.conf.urls.static import static

from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^survey_page$', 'app.views.survey_page'),
                       url(r'^welcome$', 'app.views.welcome'),
                       url(r'^submit_survey$', 'app.views.submit_survey'),
                       url(r'^thanks$', 'app.views.thanks'),
                       url(r'^finish$', 'app.views.finish'),
                       url(r'^$', 'app.views.landing'),

                       ) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
