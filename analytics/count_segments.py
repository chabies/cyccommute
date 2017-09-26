#This function counts segments from file_to_segment id dictionary and save the result in the segmentcounts table of the database

def count_segment(request, SegmentCounts, file_to_segment_list):
    j = 0
    seg_counts = {}  # {'segment_id': number of occurrence, ..., 'segment_id': number of occurrence}
    for seg_list in file_to_segment_list.itervalues():  # {"fileid":[segment_id,...,], ...,}
        for seg in seg_list:
            counts = seg_counts.get(seg, 0) + 1
            seg_counts[seg] = counts
            #print "segcounts exist?", SegmentCounts.objects.all().exists()
    for seg, counts in seg_counts.iteritems():
        if SegmentCounts.objects.filter(user=request.user, segment_id=seg).exists():
            previouscts = SegmentCounts.objects.filter(user=request.user).values_list('segment_counts', flat=True).get(
                segment_id=seg)
            SegmentCounts.objects.filter(user=request.user, segment_id=seg).update(segment_counts=previouscts + counts)
            #print "previouscts", previouscts
        else:
            a = SegmentCounts(user=request.user, segment_id=seg, segment_counts=counts)
            a.save()

        #j += 1
    #print "seg_count", j, seg_counts
    return seg_counts
