# This code has been modified to be run within this project.
# Modified block was commented on top of the relevant block.
# Source: https://github.com/mapillary/map_matching/blob/master/LICENSE
# Modification date: 20/July/2017

# The following document was written by the original creator of this script
__doc__ = '''
usage: python2 map_matcher.py PSQL_URI ROAD_TABLE_NAME [SEARCH_RADIUS = 30] [MAX_ROUTE_DISTANCE = 2000] < sequence.txt

The PSQL_URI looks like:
    "host=localhost port=5432 dbname=road_network user=postgres password=secret"

ROAD_TABLE_NAME is the table imported by osm2pgrouting.

SEARCH_RADIUS is a range value in meters within which the program will
search for each measurement's candidates. Think of it as GPS accuracy.

MAX_ROUTE_DISTANCE is the maximum allowed route distance (in meters)
between two concussive measurements.

The the input should be a list of coordinates like this:

    13.5258287 52.42294143
    13.52582773 52.42294161
    13.52582789 52.42294315
    13.5258275 52.42294331
    13.52571846 52.42293282
    13.52554795 52.42294917
    13.5255389 52.42301208
    13.52550688 52.4230304
    ...

Each line consists of a longtitude followed by a whitespace and then a
latitude.'''


import sys
import psycopg2

import map_matching as mm
from utils import Edge, Measurement

import numpy as np

def MahalanobisDist(x, y):
    covariance_xy = np.cov(x, y, rowvar=0)
    inv_covariance_xy = np.linalg.inv(covariance_xy)
    xy_mean = np.mean(x), np.mean(y)
    x_diff = np.array([x_i - xy_mean[0] for x_i in x])
    y_diff = np.array([y_i - xy_mean[1] for y_i in y])
    diff_xy = np.transpose([x_diff, y_diff])

    md = []
    for i in range(len(diff_xy)):
        md.append(np.sqrt(np.dot(np.dot(np.transpose(diff_xy[i]), inv_covariance_xy), diff_xy[i])))
    return md


def MD_removeOutliers(x, y):
    MD = MahalanobisDist(x, y)
    threshold = np.mean(MD) * 1.5  # adjust 1.5 accordingly
    nx, ny, outliers = [], [], []
    for i in range(len(MD)):
        if MD[i] <= threshold:
            nx.append(x[i])
            ny.append(y[i])
        else:
            outliers.append(i)  # position of removed pair
    return (np.array(nx), np.array(ny), np.array(outliers))


def generate_placeholder(length, width):
    """
    Generate "(%s, %s, %s, ...), ..." for placing parameters.
    """
    return ','.join('(' + ','.join(['%s'] * width) + ')' for _ in range(length))


def create_sequence_subquery(length, columns):
    """Create a subquery for sequence."""
    placeholder = generate_placeholder(length, len(columns))
    subquery = 'WITH sequence {columns} AS (VALUES {placeholder})'.format(
        columns='(' + ','.join(columns) + ')',
        placeholder=placeholder)
    return subquery


def query_edges_in_sequence_bbox(conn, road_table_name, sequence, search_radius):
    """
    Query all road edges within the bounding box of the sequence
    expanded by search_radius.
    """
    if not sequence:
        return

    subquery = create_sequence_subquery(len(sequence), ('lon', 'lat'))

    stmt = subquery + '''
    -- NOTE the length unit is in km
    SELECT edge.gid, edge.source, edge.target, edge.length * 1000, edge.length * 1000
    FROM {road_table_name} AS edge
         CROSS JOIN (SELECT ST_Extent(ST_MakePoint(sequence.lon, sequence.lat))::geometry AS extent FROM sequence) AS extent
    WHERE edge.the_geom && ST_Envelope(ST_Buffer(extent.extent::geography, %s)::geometry)
    '''.format(road_table_name=road_table_name)

    # Aggregate and flatten params
    params = sum([[lon, lat] for lon, lat in sequence], [])
    params.append(search_radius)

    cur = conn.cursor()
    cur.execute(stmt, params)

    for gid, source, target, cost, reverse_cost in cur.fetchall():
        edge = Edge(id=gid,
                    start_node=source,
                    end_node=target,
                    cost=cost,
                    reverse_cost=reverse_cost)
        yield edge

    cur.close()


def build_road_network(edges):
    """Construct the bidirectional road graph given a list of edges."""
    graph = {}

    # Graph with bidirectional edges
    for edge in edges:
        graph.setdefault(edge.start_node, []).append(edge)
        graph.setdefault(edge.end_node, []).append(edge.reversed_edge())

    return graph


# Subclass the native Candidate class to support more attributes
class Candidate(mm.Candidate):
    def __init__(self, measurement, edge, location, distance):
        super(Candidate, self).__init__(measurement=measurement, edge=edge, location=location, distance=distance)
        self.lon = None
        self.lat = None


def query_candidates(conn, road_table_name, sequence, search_radius):
    """
    Query candidates of each measurement in a sequence within
    search_radius.
    """
    subquery = create_sequence_subquery(len(sequence), ('id', 'lon', 'lat'))

    subquery = subquery + ',' + '''
    --- WITH sequence AS (subquery here),
    seq AS (SELECT *,
                   ST_SetSRID(ST_MakePoint(sequence.lon, sequence.lat), 4326) AS geom,
                   ST_SetSRID(ST_MakePoint(sequence.lon, sequence.lat), 4326)::geography AS geog
        FROM sequence)
    '''

    stmt = subquery + '''
    SELECT seq.id, seq.lon, seq.lat,
           --- Edge information
           edge.gid, edge.source, edge.target,
           edge.length, edge.length,

           --- Location, a float between 0 and 1 representing the location of the closest point on the edge to the measurement.
           ST_LineLocatePoint(edge.the_geom, seq.geom) AS location,

           --- Distance in meters from the measurement to its candidate's location
           ST_Distance(seq.geog, edge.the_geom::geography) AS distance,

           --- Candidate's location (a position along the edge)
           ST_X(ST_ClosestPoint(edge.the_geom, seq.geom)) AS clon,
           ST_Y(ST_ClosestPoint(edge.the_geom, seq.geom)) AS clat

    FROM seq CROSS JOIN {road_table_name} AS edge
    WHERE edge.the_geom && ST_Envelope(ST_Buffer(seq.geog, %s)::geometry)
          AND ST_DWithin(seq.geog, edge.the_geom::geography, %s)
    '''.format(road_table_name=road_table_name)

    # Aggregate and flatten params
    params = sum([[idx, lon, lat] for idx, (lon, lat) in enumerate(sequence)], [])
    params.append(search_radius)
    params.append(search_radius)

    cur = conn.cursor()
    cur.execute(stmt, params)

    for mid, mlon, mlat, \
        eid, source, target, cost, reverse_cost, \
        location, distance, \
        clon, clat in cur:

        measurement = Measurement(id=mid, lon=mlon, lat=mlat)

        edge = Edge(id=eid, start_node=source, end_node=target, cost=cost, reverse_cost=reverse_cost)

        assert 0 <= location <= 1
        candidate = Candidate(measurement=measurement, edge=edge, location=location, distance=distance)

        # Coordinate along the edge (not needed by MM but might be
        # useful info to users)
        candidate.lon = clon
        candidate.lat = clat

        yield candidate

    cur.close()


def map_match(conn, road_table_name, sequence, search_radius, max_route_distance):
    """Match the sequence and return a list of candidates."""

    # Prepare the network graph and the candidates along the sequence
    edges = query_edges_in_sequence_bbox(conn, road_table_name, sequence, search_radius)
    network = build_road_network(edges)
    candidates = query_candidates(conn, road_table_name, sequence, search_radius)

    # If the route distance between two consive measurements are
    # longer than `max_route_distance` in meters, consider it as a
    # breakage
    matcher = mm.MapMatching(network.get, max_route_distance)

    # Match and return the selected candidates along the path
    return list(matcher.offline_match(candidates))

#This block was modified not to use argv for runing this script but inside this project with the input parameters
'''def parse_argv(argv):
    argv = argv[:] + [None, None]
    try:
        uri, road_table_name, search_radius, max_route_distance = argv[:4]
        search_radius = 30 if search_radius is None else int(search_radius)
        max_route_distance = 2000 if max_route_distance is None else int(max_route_distance)
    except ValueError:
        print >> sys.stderr, __doc__
        return

    return uri, road_table_name, search_radius, max_route_distance'''

#This block was modified to include input_list to run it inside this project
def main(uri, road_table_name, search_radius, max_route_distance, input_list):
    #params = parse_argv(argv)
    #if not params:
        # Something is wrong
    #    return 1
    #uri, road_table_name, search_radius, max_route_distance = params

    #sequence = [map(float, line.strip().split()) for line in sys.stdin if line.strip()]
    sequence = input_list
    conn = psycopg2.connect(uri)
    candidates = map_match(conn, road_table_name, sequence, search_radius, max_route_distance)
    conn.close()
    matching_ways_gid = []
    i=0
    for candidate in candidates:
        #print '         Measurement ID: {0}'.format(candidate.measurement.id)
        #print '             Coordinate: {0:.6f} {1:.6f}'.format(*map(float, (candidate.measurement.lon, candidate.measurement.lat)))
        #print '    Matched coordinate: {0:.6f} {1:.6f}'.format(*map(float, (candidate.lon, candidate.lat)))
        #print '        Matched edge ID: {0}'.format(candidate.edge.id) #Comment by BCHA: This is matched segment id in OSM data in the database
        #print 'Location along the edge: {0:.2f}'.format(candidate.location)
        #print '               Distance: {0:.2f} meters'.format(candidate.distance)
        #print

        if candidate.edge.id not in matching_ways_gid:
            matching_ways_gid.append(candidate.edge.id)
        i += 1
    '''
    #This is to get {gid:matching coordinates, ... , }
    matching_ways_gid_coords = {}
    for gid in matching_ways_gid:
        list_matching_coordinates_for_gid = []
        for candidate in candidates:
            if candidate.edge.id == gid:
                list_matching_coordinates_for_gid.append([candidate.lon, candidate.lat])
        matching_ways_gid_coords[gid] = list_matching_coordinates_for_gid
        #print matching_ways_gid_coords'''

    #Matching test/ This is to get a list of matching coordinates
    matching_coordinates = []
    for candidate in candidates:
        matching_coordinates.append([candidate.lat, candidate.lon])
        #print matching_coordinates

    '''
    for candidate in candidates:
        for outlier in matching_outliers:
            #print "asdf",outlier, [candidate.lat, candidate.lon]
            if [candidate.lat, candidate.lon] != outlier:
                if candidate.edge.id not in matching_ways_gid:
                    matching_ways_gid.append(candidate.edge.id)
    #print "FINAL_GID", matching_ways_gid'''

    #print "matching", i
    return {0:matching_ways_gid, 1:matching_coordinates}

# This is to run this script by the input parameters in the matching_to_network.py
if __name__ == '__main__':
    main(uri, road_table_name, search_radius, max_route_distance, input_list)
