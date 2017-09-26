from django.core.serializers import serialize
from. models import GPXFile, Ways
from mapmatching.map_matching import map_matcher
import json
def matching_segments(request, gpxfiles, user_data):
    gpxfile_id_list = []
    for i in range(len(gpxfiles)):
        gpxfile_id_list.append(gpxfiles[i].id)

    uri = "host=localhost port=5432 dbname=test_route_group user=postgres password=1024"
    road_table_name = "ways"
    search_radius = 30
    max_route_distance = 2000

    matching_coordinates = {}  # {'fileid':[coords,...,],...,}
    file_to_segment_list = {}  # {"fileid":[segment_id,...,], ...,}
    file_to_segment_geojson = {}  # {"fileid":geojson of segments, ..., }

    q = 0
    for fileid in gpxfile_id_list:
        input_list = []
        user_data_for_id = user_data.filter(gpxfile=fileid)
        for i in range(len(user_data_for_id)):
            input_list.append([user_data_for_id[i].point.x, user_data_for_id[i].point.y])
        matching_results = map_matcher.main(uri, road_table_name, search_radius, max_route_distance,
                                            input_list)  # {gid(1) of ways table: list of matching points for each input, ... , gid(n): [[lon,lat],..,[lon,lat]]}

        matching_coordinates[fileid] = matching_results[1] # For plotting on the map as a test
        # q += 1
        # print "received matching results!", q

        # Until this point, the map matching was processed for the uploaded files
        # However, counting should be for accumulated data held by the user.
        # Therefore, the whole data held by the user should be loaded, which will be file_to_segment dictionary
        segments = Ways.objects.filter(gid__in=matching_results[0])  # matched segments
        file_to_segment_geojson[fileid] = serialize('geojson', segments)
        file_to_segment_list[fileid] = list(segments.values_list('gid', flat=True))  # [gid of segment, ..., ]
        segments_json=json.dumps(list(segments.values_list('gid', flat=True)))
        #print "file_to_segment_list", file_to_segment_list

        #save the segment geojson in the gpxfile table
        GPXFile.objects.filter(user=request.user, pk=fileid).update(segments=segments_json)
    return {0:file_to_segment_list, 1:file_to_segment_geojson, 2:matching_coordinates}