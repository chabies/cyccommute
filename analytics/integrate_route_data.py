#This function calculate average travel time for each route by averaging travel times of the files grouped into the route.
#This also generates a random colour for the route, counts how many times the route was ridden by counting the files belonging to the route.
#Those average travel time, colour and counts of the route are saved to the route table of the database.
#Route colour and route ID are appended to each segment of the route and the resultant segments GeoJSON is saved to the segmentgeojson table.

import randomcolor
import json
from .models import GPXFile
def integrate_route_data(request, RouteCounts, SegmentGeoJSON, route_group_list, traveltime, file_to_segment_geojson):
    l = 0
    route_counts = {}  # {'route_id': number of occurrence, ..., }
    for routeID, v in route_group_list.iteritems():  # {"0":{"fileid":[segid,...,], ..., }, ..., }
        # comapre with file-traveltime and make route-average traveltime
        tt_list = []
        for fileID, tt in traveltime.iteritems():
            if fileID in v.iterkeys():
                tt_list.append(tt)
        if len(tt_list) == 0:
            continue
        else:
            avg_tt = sum(tt_list) / len(tt_list)

        # generate a random color
        rcolor = randomcolor.RandomColor().generate(luminosity='dark', hue='random')[0]

        # count the number of files for each route and give it a color
        counts = len(v)
        route_color = rcolor
        route_counts[routeID] = {"counts": counts, "route_color": route_color, "route_tt": avg_tt}
        if RouteCounts.objects.filter(user=request.user, route_id=routeID).exists():
            RouteCounts.objects.filter(user=request.user, route_id=routeID).update(route_counts=counts, route_tt=avg_tt)

        else:
            a = RouteCounts(user=request.user, route_id=routeID, route_counts=counts, route_color=route_color,
                            route_tt=avg_tt)
            a.save()

        route_color = RouteCounts.objects.filter(user=request.user).values_list('route_color', flat=True).get(
            route_id=routeID)

        # append routeID and route color to properties
        for fid in v.iterkeys():  # ["fileid", ..., ]
            print fid
            for fileid in file_to_segment_geojson.iterkeys():  # dict of unicode, {"fileid":geojson of segments, ..., }
                geojson = file_to_segment_geojson[fileid]  # unicode
                geojson = json.loads(geojson)
                if fileid == fid:
                    features_value = geojson['features']
                    for feature in features_value:
                        properties = feature['properties']
                        properties['routeID'] = routeID
                        properties['route_color'] = route_color
                    geojson = json.dumps(geojson)

                    a = SegmentGeoJSON(gpxfile=GPXFile.objects.get(pk=fileid), user=request.user, geojson=geojson)
                    a.save()

                #l += 1
        #print "route_count", l
    #print "route_counts", route_counts
    return route_counts