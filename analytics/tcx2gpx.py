"""This script was modified to be used inside of this project and to reformat the output gpx files.
Modification date: 2017/07/31
The source information is as following.
"""

"""Simple converter from TCX file to GPX format

Usage:   python tcx2gpx.py   foo.tcx  > foo.gpx

Streaming implementation works for large files.

Open Source: MIT Licencse.
This is or was <http://www.w3.org/2009/09/geo/tcx2gpx.py>
Author: http://www.w3.org/People/Berners-Lee/card#i
Written: 2009-10-30
Last change: $Date: 2009/10/28 13:44:33 $
"""
import urllib
from xml import sax
from xml.sax import saxutils
import sys, os


def output_set(output_file):
    global fl
    fl = open(output_file, 'w')

TCX_NS = "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"


class MyHandler(sax.handler.ContentHandler):

    def __init__(self):
        self.time = ""
        self.lat = ""
        self.lon = ""
        self.alt = ""
        self.content = ""

    def startDocument(self):
        fl.write("""<gpx xmlns="http://www.topografix.com/GPX/1/1"
    creator="http://www.w3.org/2009/09/geo/tcx2gpx.py"
    version="1.1"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">
""")

    def endDocument(self):
        fl.write('</gpx>\n')

    def startElement(self, name, attrs):

        self.content = ""
        if name == 'Track':
            fl.write(' <trk>\n')

    def characters(self, content):
        self.content = self.content + saxutils.escape(content)

    #    def endElementNS(fname, qname, attrs):
    #        (ns, name) = fname

    def endElement(self, name):
        if name == 'Track':
            fl.write(' </trk>\n')
        elif name == 'Trackpoint':
            fl.write('  <trkpt lat="%s" lon="%s">\n' % (self.lat, self.lon))
            if (self.alt): fl.write('   <ele>%s</ele>\n' % self.alt)
            if (self.time): fl.write('   <time>%s</time>\n' % self.time)
            fl.write('  </trkpt>\n')
            sys.stdout.flush()
        elif name == 'LatitudeDegrees':
            self.lat = self.content
        elif name == 'LongitudeDegrees':
            self.lon = self.content
        elif name == 'AltitudeMeters':
            self.alt = self.content
        elif name == 'Time':
            self.time = self.content

def close_fl():
    fl.close()

handler = MyHandler()


def read_TCX(uri):
    sax.parse(uri, handler)

if __name__ == '__main__':
    read_TCX(uri)

# ends