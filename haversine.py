import numpy as np

def haversine(lon0,lon1,lat0,lat1):
    r = 6371000. # m
    lon0 = lon0*np.pi/180
    lon1 = lon1*np.pi/180
    lat0 = lat0*np.pi/180
    lat1 = lat1*np.pi/180

    return 2*r*np.arcsin(np.sqrt(np.sin((lat1 - lat0)/2.)**2 + np.cos(lat0)*np.cos(lat1)*np.sin((lon1 - lon0)/2.)**2))
