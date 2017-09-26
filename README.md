# cyccommute
a web platform for visual analytics of individual commuter cyclists data

This project was initiated as a work for a Master's disseration of BCHA in MSc GIS in University College London.
The completion date of the current version is 13th September, 2017.

The web platform visualises riding frequecy of certain OSM (OpenStreetMap) road segments and routes and traveltimes of routes which are computated from user-uploaded GPS log files (gpx and/or tcx files).

In order to test the web platform, the following steps should be done:

[1] Preparation of web framework and database
1.Install GeoDjango and PostgreSQL (with PostGIS) (https://docs.djangoproject.com/en/1.11/ref/contrib/gis/install/).
2.Create a database together with postgis and pgrouting extensions.
3.Mount the OpenStreetMap road network osm file that is included in this repository by using the osm2pgrouting (osm2pgrouting for use on Windows can be downloaded at http://winnie.postgis.net/download/windows/pg95/buildbot/ for the postgresql 9.5. You can find other versions in the result of the search).
4.Set the connection parameters to the database in the setting.py of the project (under the cyclist folder).
5.Set the connection parameters to the database in the map_matching.py under the ananlytics folder.

[2] Install dependancy and migrate models
6.Install all the Python libraries using the following command line:
  pip install "library" (library: geopy, numpy, randomcolor)
7.Migrate models by the following command lines:
  python manage.py makemigrations
  python manage.py migrate

[3] Test the platform
8. Resister a test user through the resister menu.
9. Upload a zip file on the add route page.
10. Check the visual analytics on the map page.
11. You can upload different combination of tcx files to see if the result is updated accordingly on the map and charts.

The major problems that were found are:
1. Fragmentation of trajectories due to the matter of performance of the map matching.
2. Difficult distinction of overlapping routes on the map.

These can be improved by:
1. Adapting a better performing map matching.
2. Interactive effect on the each bar of the bar charts which highlights the corresponding route on the map.
