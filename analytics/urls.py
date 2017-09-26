#This contains url patterns to be recognised by the url requested from the browser and to call the corresponding view.

from django.conf.urls import url
from . import views


app_name = 'analytics'

urlpatterns = [

    #/analytics/
    url(r'^$', views.main, name = 'main'),

    #/analytics/mycommute/
    url(r'^mycommute/$', views.MycommuteView.as_view(), name = 'mycommute'),

    #/analytics/mycommute/process_gpsdata/
    url(r'^mycommute/process_gpsdata/$', views.process_gpsdata, name = 'process_gpsdata'),

    #/analytics/json_data/
    url(r'^json_data/$', views.json_data, name ='json_data'),

    #/analytics/register/
    url(r'^register/$', views.user_register, name='register'),

    #/analytics/login_user/
    url(r'^login_user/$', views.login_user, name='login_user'),

    #/analytics/logout_user/
    url(r'^logout_user/$', views.logout_user, name='logout_user'),



]