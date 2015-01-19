'''
This file will download and convert the proper USGS elevation
data and covert it to a STereoLithograph format.
'''

import numpy as np
from osgeo import gdal # To open GridFloat format
from downloadElevUSGS import downloadElevUSGS
from haversine import haversine

# Define Point of Interest (POI) Latitude and Longitude

POILat = 40.254883
POILon = -105.616118
radius = 3. # km

mapResolution = '13'
mapName = 'terrain.stl'

baseElev = 0. #m

# Download the proper files from the USGS FTP server

downloadElevUSGS(np.ceil(POILat),np.ceil(abs(POILon)),mapResolution)

# Open the USGS file

f = gdal.Open("n%02dw%03d/floatn%02dw%03d_%s.flt" % (np.ceil(POILat),np.ceil(abs(POILon)),np.ceil(POILat),np.ceil(abs(POILon)),mapResolution))

elev = f.ReadAsArray()

coords = f.GetGeoTransform()
PLat = [0,1]
PLon = [1,0]

lons = np.arange(coords[0],coords[0] + (PLon[0]*coords[1] + PLon[1]*coords[2])*(len(elev)-1),PLon[0]*coords[1] + PLon[1]*coords[2])

lats = np.arange(coords[3],coords[3] + (PLat[0]*coords[4] + PLat[1]*coords[5])*len(elev[0]),PLat[0]*coords[4] + PLat[1]*coords[5])

Dx = haversine(POILon,lons,POILat,POILat)/1000.
Dy = haversine(POILon,POILon,POILat,lats)/1000.

relevantIndicesX = np.where(Dx <= radius)[0]
relevantIndicesY = np.where(Dy <= radius)[0]

LONS,LATS = np.meshgrid(lons[relevantIndicesX],lats[relevantIndicesY])
X,Y = haversine(LONS[0,0],LONS,LATS[0,0],LATS[0,0]), haversine(LONS[0,0],LONS[0,0],LATS[0,0],LATS)
zoomElev = elev[relevantIndicesY[0]:relevantIndicesY[-1]+1,relevantIndicesX[0]:relevantIndicesX[-1]+1]
zoomElev = zoomElev - zoomElev.min()

fileSTL = open(mapName,'wb')
stl_str = 'solid terrain\n'

def make_facet_str( n, v1, v2, v3 ):
    facet_str = 'facet normal ' + ' '.join( map(str,n) ) + '\n'
    facet_str += ' outer loop\n'
    facet_str += ' vertex ' + ' '.join( map(str,v1) ) + '\n'
    facet_str += ' vertex ' + ' '.join( map(str,v2) ) + '\n'
    facet_str += ' vertex ' + ' '.join( map(str,v3) ) + '\n'
    facet_str += ' endloop\n'
    facet_str += 'endfacet\n'
    return facet_str

for i in range(len(zoomElev)-1):
    for j in range(len(zoomElev[0])-1):

        v1 = [X[i,j],Y[i,j],zoomElev[i,j]]
        v2 = [X[i,j+1],Y[i,j+1],zoomElev[i,j+1]]
        v3 = [X[i+1,j],Y[i+1,j],zoomElev[i+1,j]]
        v4 = [X[i+1,j+1],Y[i+1,j+1],zoomElev[i+1,j+1]]

        # dem facet 1
        n = np.cross( np.array(v1)-np.array(v2), np.array(v1)-np.array(v3) )
        n = n / np.sqrt( np.sum( n**2 ) )
        stl_str += make_facet_str( n, v1, v2, v3 )
        # dem facet 2
        n = np.cross( np.array(v2)-np.array(v3), np.array(v2)-np.array(v4) )

        n = n / np.sqrt( np.sum( n**2 ) )
        n[-1] = n[-1]*-1
        stl_str += make_facet_str( n, v2, v4, v3 )
        #base facets
        v1[-1] = baseElev
        v2[-1] = baseElev
        v3[-1] = baseElev
        v4[-1] = baseElev
        n = [0.0,0.0,-1.0]
        stl_str += make_facet_str( n, v1, v3, v2 )
        stl_str += make_facet_str( n, v2, v3, v4 )

#WEST

for j in range(len(zoomElev[0])-1):
    v1 = [X[0,j],Y[0,j],baseElev]
    v2 = [X[0,j+1],Y[0,j+1],baseElev]
    v3 = [X[0,j],Y[0,j],zoomElev[0,j]]
    v4 = [X[0,j+1],Y[0,j+1],zoomElev[0,j+1]]
    n = [-1,0,0]
    stl_str += make_facet_str( n, v1, v2, v3 )
    stl_str += make_facet_str( n, v2, v4, v3 )

#EAST

for j in range(len(zoomElev[0])-1):
    v1 = [X[-1,j],Y[-1,j],baseElev]
    v2 = [X[-1,j+1],Y[-1,j+1],baseElev]
    v3 = [X[-1,j],Y[-1,j],zoomElev[-1,j]]
    v4 = [X[-1,j+1],Y[-1,j+1],zoomElev[-1,j+1]]
    n = [1,0,0]
    stl_str += make_facet_str( n, v1, v3, v2 )
    stl_str += make_facet_str( n, v2, v3, v4 )

#SOUTH

for i in range(len(zoomElev)-1):
    v1 = [X[i,0],Y[i,0],baseElev]
    v2 = [X[i+1,0],Y[i+1,0],baseElev]
    v3 = [X[i,0],Y[i,0],zoomElev[i,0]]
    v4 = [X[i+1,0],Y[i+1,0],zoomElev[i+1,0]]
    n = [0,-1,0]
    stl_str += make_facet_str( n, v1, v3, v2 )
    stl_str += make_facet_str( n, v2, v3, v4 )

#NORTH

for i in range(len(zoomElev)-1):
    v1 = [X[i,-1],Y[i,-1],baseElev]
    v2 = [X[i+1,-1],Y[i+1,-1],baseElev]
    v3 = [X[i,-1],Y[i,-1],zoomElev[i,-1]]
    v4 = [X[i+1,-1],Y[i+1,-1],zoomElev[i+1,-1]]
    n = [0,1,0]
    stl_str += make_facet_str( n, v1, v2, v3 )
    stl_str += make_facet_str( n, v2, v4, v3 )


stl_str += 'endsolid terrain\n'
fileSTL.write(stl_str)
fileSTL.close()
