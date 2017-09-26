# -*- coding: utf-8 -*-
# This contains views which receive a request and response with the processed data to the templates.

from __future__ import unicode_literals
from django.contrib.auth import logout

from django.views.generic import TemplateView
from django.core.serializers import serialize
from django.http import HttpResponse

## user login
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login #autthenticate varifies if the user is registered in db / login attatches a session id wichi is used for browing id without needing to login everytime
from .forms import UserForm, FileUploadForm # import UserForm class

import os

from .models import GPXPoint, GPXFile, SegmentGeoJSON, SegmentCounts, Route, MatchingPoint
from cyclist.settings import BASE_DIR

import zipfile

from django.db.models.signals import pre_save

import json

from django.contrib.gis.utils import LayerMapping

from tcx2gpx import MyHandler, output_set, close_fl
from xml import sax

from matching_to_network import matching_segments
from extract_traveltime import extract_traveltime
from integrate_route_data import integrate_route_data
from segments_to_routes import segments_to_routes
from count_segments import count_segment

from django.contrib.gis.geos import Point

def main(request):
    if not request.user.is_authenticated():
        return render(request, 'analytics/login.html')
    else:
        files = GPXFile.objects.filter(user=request.user)
        return render(request, 'analytics/main.html', {'files': files})

    template_name = 'analytics/mycommute.html'
#This takes a request consisting of username, password, email typed in the form and register the user in the database.
#Afterwards, this makes the user logged in with authentication check and load the main page.
def user_register(request):
        form = UserForm(request.POST or None) # hit the submit button then the typed data is stored in POST, which is passed to the form. The form validate the data

        if form.is_valid():
            user = form.save(commit=False) # creates an object from the form but does not save it to db yet, storing just locally (commit=False)
            #clean normalised data. i.e., format it properlly (ex., unify date format typed differently by users)
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user.set_password(password)# when you need to change user's password, assign the type password to the user object (update)/should not use use.password = 'bwdjj12' because the original password is asterisk
            user.save() # save the typed user info to db

            #authenticate the user and make him login
            # return User objects if credentials are correct
            user = authenticate(username=username, password=password) # if authenticated, they are stored in user
            if user is not None:
                if user.is_active: #Django admin allows banning or disable a user, so need to check if the user is in those state
                    login(request, user) # if it is not the cases, make the user login
                    return redirect('analytics:main') # then return the home screen
        return render(request, 'analytics/registration_form.html', {'form': form}) # the user is banned to login or fail to be credential, show the black form

#This receives the POST request containing a set of username and password and make the user logged in after authetication.
def login_user(request):
    form = UserForm(request.POST or None)
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                files = GPXFile.objects.filter(user=request.user)
                return render(request, 'analytics/main.html', {'files': files})
            else:
                return render(request, 'analytics/login.html', {'error_message': 'Your account has been disabled'})
        else:
            return render(request, 'analytics/login.html', {'error_message': 'Invalid login'})
    return render(request, 'analytics/login.html', {'form': form})

# This makes the user logout when the user click the logout button to make a request to this and load the login page
def logout_user(request):
    logout(request)
    form = UserForm(request.POST or None)
    context = {
        "form": form,
    }
    return render(request, 'analytics/login.html', context)

#For loading the map page
class MycommuteView(TemplateView):
    template_name = 'analytics/mycommute.html'

#To process data: upzip, save gpx files to the database, map matching, save the map matching results to the database
def process_gpsdata(request):

    point_mapping = {'point': 'POINT',
                     'timestamp': 'time',
                     }
    #Once the form is valid, unzip the submitted zip file
    form = FileUploadForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        #unzip
        zipgpx = form.save(commit=False)
        zipgpx.filename = request.FILES['filename'] #get file name
        zipgpx.user = request.user
        zipgpx.save() # file save and in dababase
        zippath = BASE_DIR + '\\analytics\\routefiles'+'\\' + str(zipgpx.filename)
        zip = zipfile.ZipFile(zippath)
        unzippath = BASE_DIR + '\\analytics\\routefiles\\'+ str(request.user) + '\\' + str(zipgpx.id) # unzip in the user's folder which is created at the same time in the name of the current zipfile id/if the folder or files already exists, it overwrites.
        zip.extractall(unzippath)

        #delete the uploded zipfile
        #zip.close()
        #os.remove(unzippath)

        ##save all the unzipped files into the database
        #If some of the files are .tcxs, they are converted into .gpxs by the tcx2gpx.py
        for (root, dirs, filenames) in os.walk(unzippath):
            for f in filenames:
                if f.endswith(".tcx"):
                    tcx_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'routefiles/'+str(request.user)+'/'+ str(zipgpx.id) +'/'+ str(f)))
                    output = os.path.abspath(os.path.join(os.path.dirname(__file__), 'routefiles/'+str(request.user)+'/'+ str(zipgpx.id) +'/'+ str(f).replace("tcx","gpx")))
                    output_set(output)
                    handler = MyHandler()
                    sax.parse(tcx_file, handler)
                    close_fl()

        #Read all the gpx files and save them in the database via LayerMapping
        gpxidlist = []
        for (root, dirs, filenames) in os.walk(unzippath):
            for f in filenames:
                if f.endswith(".gpx"):
                    gpx_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'routefiles/'+str(request.user)+'/'+ str(zipgpx.id) +'/'+ str(f)))
                    lm_tr = LayerMapping(GPXPoint, gpx_file, point_mapping, layer='track_points')
                    gpxfile = GPXFile(user=request.user, filename=str(f))
                    gpxfile.save()
                    gpxidlist.append(gpxfile.pk)
                    #source: https://stackoverflow.com/questions/22324752/django-connect-temporary-pre-save-signal
                    #This is to fill the user field while each row is being populated by layermapping
                    def pre_save_callback(sender, instance, *args, **kwargs):
                        instance.user = request.user # set an instance of the model field and impose value to it which will fill the field this process.
                        instance.gpxfile = gpxfile
                    pre_save.connect(pre_save_callback, sender=GPXPoint)
                    try:
                        lm_tr.save(strict=True)
                    finally:
                        pre_save.disconnect(pre_save_callback, sender=GPXPoint)

        # take the gpxfile objects and gpxpoint objects only for the current user
        user_gpxfiles = GPXFile.objects.filter(user=request.user)
        gpxfiles_of_uploadded = user_gpxfiles.filter(pk__in=gpxidlist) #uploaded gpxfiles
        user_points = GPXPoint.objects.filter(user=request.user)
        #print "took files from db"

        #map matching to OSM network and update gpxfile table with matched segments
        matching_segments_returns = matching_segments(request, gpxfiles_of_uploadded, user_points)
        file_to_segment_list = matching_segments_returns[0]
        file_to_segment_geojson = matching_segments_returns[1]

        #This is for checking matching points
        file_to_coordsliest = matching_segments_returns[2]  # {fileid: [[lat,lng], ..., ], ..., }
        for fileid, latlng_list in file_to_coordsliest.items():
            for latlng in latlng_list:
                point = Point(latlng[1], latlng[0], srid=4326)
                p = MatchingPoint(user=request.user, gpxfile=GPXFile.objects.get(pk=fileid), point=point)
                p.save()
        #for k in file_to_segment_geojson:
            #print "file_to_geojson_k", k

        #count segment and save it to the database
        count_segment(request, SegmentCounts, file_to_segment_list)

        # Grouping files as routes by similarity between segments
        gpxfiles = GPXFile.objects.filter(user=request.user).values('pk','segments')
        gfs = {}
        for i in range(len(gpxfiles)):
            fileid = gpxfiles[i]['pk']
            segments = json.loads(gpxfiles[i]['segments'])
            #print 'pk', type(fileid), fileid
            #print 'jlosd', type(segments), segments
            gfs[fileid] = segments
        route_group_list = segments_to_routes(gfs)

        #This extract travel times of gpxfiles
        traveltime = extract_traveltime(user_points, user_gpxfiles)

        # make a dictionary of routeID to average travel time {routeID:average travel time over files, ...,}
        integrate_route_data(request, Route, SegmentGeoJSON, route_group_list, traveltime, file_to_segment_geojson)

        return render(request, 'analytics/mycommute.html')

    context = {"form": form,}
    return render(request, 'analytics/upload_files.html', context)

def json_data(request):
    #This is to retrieve the processed data from the database (segments GeoJSONs, segment counts, route data)
    geojson = SegmentGeoJSON.objects.filter(user=request.user)
    segcounts = SegmentCounts.objects.filter(user=request.user)
    routecounts = Route.objects.filter(user=request.user)

    # To retrieve GeoJSONs of matching segments
    segments_geojson = {}
    for fileid in list(geojson.values_list('gpxfile', flat=True)):
        segments_geojson[fileid] = geojson.values_list('geojson', flat=True).get(gpxfile=fileid)

    # To retrieve counts of segments
    seg_counts ={}
    for segid in list(segcounts.values_list('segment_id', flat=True)):
        seg_counts[segid] = segcounts.values_list('segment_counts', flat=True).get(segment_id=segid)

    #To read the input GPS points for the purpose of checking them on the map
    route_data={}
    for routeid in list(routecounts.values_list('route_id', flat=True)):
        route_data[routeid] = {"counts": routecounts.values_list('route_counts', flat=True).get(route_id=routeid),
                                 "route_color": routecounts.values_list('route_color', flat=True).get(route_id=routeid),
                                 "route_tt": routecounts.values_list('route_tt', flat=True).get(route_id=routeid)}


    gpxfiles = GPXFile.objects.filter(user=request.user)

    #This is to read the input GPS points for the purpose of checking them on the map
    user_data = GPXPoint.objects.filter(user=request.user)
    dataset = {}  # {gpxfile.id(1): GeoJSON_points(1), gpxfile.id(2): GeoJSON_points(2), ... , gpxfile.id(n): GeoJSON_point(n)}
    for i in range(len(gpxfiles)):
        dataset[i] = serialize('geojson', user_data.filter(
            gpxfile=gpxfiles[i].pk))  # make the spatial data in model (Class) into geojsonformat

    # To read the matching points for the purpose of checking them on the map
    matching_points = MatchingPoint.objects.filter(user=request.user)
    matching_points_geojson = {}  # {gpxfile.id(1): GeoJSON_points(1), gpxfile.id(2): GeoJSON_points(2), ... , gpxfile.id(n): GeoJSON_point(n)}
    for i in range(len(gpxfiles)):
        matching_points_geojson[i] = serialize('geojson', matching_points.filter(
            gpxfile=gpxfiles[i].pk))  # make the spatial data in model (Class) into geojsonformat

    return HttpResponse(json.dumps({'segments_geojson':segments_geojson, 'seg_counts':seg_counts, 'route_data':route_data, 'dataset':dataset, 'matching_points_geojson':matching_points_geojson}))