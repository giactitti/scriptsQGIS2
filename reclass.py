# coding: utf-8
##Reclassification=name
##Wcause=raster
##Wreclassed= output raster
##classes=file

import numpy as np
from osgeo import gdal
import sys
import math
import csv

def classification():
    ds = gdal.Open(Wcause)#A
    if ds is None:
        print("ERROR: can't open raster input")
    a=ds.GetRasterBand(1)
    #print a
    NoData=a.GetNoDataValue()
    matrix0 = np.array(a.ReadAsArray())
    matrix = np.array(a.ReadAsArray())
    #print matrix
    xsize = ds.RasterXSize
    ysize = ds.RasterYSize
    bands = ds.RasterCount
    if bands>1:
        print("ERROR: input rasters shoud be 1-band raster")
    Min={}
    Max={}
    clas={}
    with open(classes, 'r') as f:
        c = csv.reader(f,delimiter=' ')
        count=1
        for cond in c:
            #print cond
            b=np.array([])
            b=np.asarray(cond)
            #print b[0]
            Min[count]=float(b[0])
            Max[count]=float(b[1])
            clas[count]=b[2].astype(int)
            #print min,max,cell_value
            count+=1
    matrix0=matrix0.astype(int)
    idx=np.where(np.isnan(matrix0))
    #print idx
    matrix[idx]=-9999
    for i in range(1,count):
        #print i
        matrix[(matrix0>=Min[i])&(matrix0<=Max[i])]=clas[i]
    #print 'end'
    return matrix,xsize,ysize,ds


def save():
    try:
        out_data = None
        # read in data from first band of input raster
        rows = xsize
        cols = ysize
        # create single-band float32 output raster
        driver = ds.GetDriver()
        out_data = driver.Create(Wreclassed, cols, rows, 1, gdal.GDT_Float32)
        if out_data is None:
            print('Could not create output file')
        # set values below nodata threshold to nodata
        dem_data = matrix
        # write the data to output file
        out_band = out_data.GetRasterBand(1)
        out_band.WriteArray(dem_data, 0, 0)
        # flush data to disk, set the NoData value and calculate stats
        out_band.FlushCache()
        out_band.SetNoDataValue(-9999)
        # georeference the image and set the projection
        out_data.SetGeoTransform(ds.GetGeoTransform())
        out_data.SetProjection(ds.GetProjection())
    except:
            print("Failure to set nodata values on raster input")
    finally:
            del out_data
            print 'end'

matrix,xsize,ysize,ds=classification()
save()