#The segments_to_routes function groups sets of segment IDs into routes by the Jaccard similarity with a threshold

import collections

#calculate Jaccard similarity between two lists
def jaccard_similarity(x, y):
    intersection_cardinality = len(set.intersection(*[set(x), set(y)]))
    union_cardinality = len(set.union(*[set(x), set(y)]))
    return intersection_cardinality / float(union_cardinality)

###group lists of segment IDs of files into route IDs
def segments_to_routes(gpxfiles):
    # Order the gpxfiles dictionary
    dic = gpxfiles #{gpxfileid:segmentlist}
    dic = collections.OrderedDict(sorted(dic.items()))
    #print "dic", dic

    threshold = 0.70
    sim_dic = collections.OrderedDict()
    # make a list of similarity indexes for each file in the form of dictionary
    for i in range(len(dic)):
        sim_list = []
        for j in range(len(dic)):
            print dic.keys()
            if i != j:
                sim = jaccard_similarity(dic.values()[i], dic.values()[j])
                print dic.values()[i], dic.values()[j], sim
            else:
                sim = 0

            sim_list.append(sim)
        sim_dic[dic.keys()[i]] = sim_list

    print sim_dic

    k = 1  # route_id
    routes = collections.OrderedDict()
    for i in range(len(sim_dic)):
        #print 'range', range(len(sim_dic))

        total_keys = []
        for value in routes.itervalues():
            for key in value.iterkeys():
                total_keys.append(key)
        # create a group for the current file ID (segment ID list)
        if sim_dic.keys()[i] not in total_keys:
            group = collections.OrderedDict()
            group[dic.keys()[i]] = dic.values()[i]
        else:
            continue

        #pick indexes of maximum similarities (plural in case multiple numbers of the same similarity)
        #and put them in the form of list
        m = max(sim_dic.values()[i])
        index_max = [x for x, y in enumerate(sim_dic.values()[i]) if y == m]
        print index_max

        # pick a pair of file ID - list of segment IDs which has the maximum similarity with the current file ID-segment ID list
        # put it in the current group
        for j in index_max:
            #print 'j', j
            #print 'i', i
            if sim_dic.keys()[i] not in total_keys:
                #print 'key', sim_dic.keys()[i], 'ls', sim_dic.values()[i]
                #print "sim", sim_dic.values()[i][j]
                if sim_dic.values()[i][j] >= threshold:
                    group[dic.keys()[j]] = dic.values()[j]
                else:
                    continue
            else:
                continue

        # upon finishing the iteration, put the current group into the route dictionary with k which is a route ID
        routes[k] = group

        k += 1

    print routes
    return routes