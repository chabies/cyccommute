# Extract travel times for each gpx file from gpx point data of the logged-in user (user_data)

def extract_traveltime(user_points, user_gpxfiles):
    timeset = {}  # {gpxfile.id:traveltime, ..., }
    for i in range(len(user_gpxfiles)):
        # dataset[i] = serialize('geojson', user_data.filter(gpxfile=gpxfiles[i].pk))  # make the spatial data in model (Class) into geojsonformat
        # print "gpxfiles[i].pk", gpxfiles[i].pk
        user_data_for_file = user_points.filter(gpxfile=user_gpxfiles[i].pk)  # timeseries for the current gpxfile
        timeseries = list(
            user_data_for_file.values_list('timestamp', flat=True).order_by('timestamp'))  # from endtime to starttime
        #print "gpxfiles_user[i].pk", gpxfiles_user[i].pk, "timeseries", timeseries, "len", len(timeseries)
        st = timeseries[0]
        et = timeseries[-1]
        tt = et - st
        tt = (tt.seconds // 60) % 60  # in minutes
        #print "st", st, "et", et
        #print "traveltime", tt
        timeset[user_gpxfiles[i].pk] = tt  # append gpxfileID:traveltime to the timeset dictionary
    #print "timeset", timeset
    return timeset
