# This file is meant to download the proper USGS elevation data

import os

def downloadElevUSGS(lat,lon,resolution):
    
    '''
    This method requires having the 'wget' command installed on your
    computer.
    '''

    os.system('wget -nc ftp://rockyftp.cr.usgs.gov/vdelivery/Datasets/Staged/NED/%s/GridFloat/n%02dw%03d.zip' % (resolution,lat,lon))

    os.system('unzip -u -d n%02dw%03d n%02dw%03d.zip' % (lat,lon,lat,lon))
