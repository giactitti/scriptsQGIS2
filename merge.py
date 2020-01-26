##Merge=name
##include_R1=Boolean True
##R1=raster
##include_R2=Boolean True
##R2=raster
##include_R3=Boolean True
##R3=raster
##include_R4=Boolean True
##R4=raster
##include_R5=Boolean True
##R5=raster
##include_R6=Boolean True
##R6=raster
##include_R7=Boolean True
##R7=raster
##include_R8=Boolean True
##R8=raster
##include_R9=Boolean True
##R9=raster
##include_R10=Boolean True
##R10=raster
##LSIout=output raster

#coding=utf-8
import numpy as np
from osgeo import gdal,osr
import sys
import math
import csv
from qgis.core import QgsMessageLog
import os

def importing():
    raster={}
    count=0
    ds1=gdal.Open(R1)
    if ds1 is None:
        print("ERROR: can't open raster input")
    if include_R1 is True: 
        raster[count] = np.array(ds1.GetRasterBand(1).ReadAsArray())
        x = ds1.RasterXSize
        y = ds1.RasterYSize
        count+=1

    ds2=gdal.Open(R2)
    if ds2 is None:
        print("ERROR: can't open raster input")
    if include_R2 is True: 
        raster[count] = np.array(ds2.GetRasterBand(1).ReadAsArray())
        count+=1
    

    ds3=gdal.Open(R3)
    if ds3 is None:
        print("ERROR: can't open raster input")
    if include_R3 is True: 
        raster[count] = np.array(ds3.GetRasterBand(1).ReadAsArray())
        count+=1
    
    ds4=gdal.Open(R4)
    if ds4 is None:
        print("ERROR: can't open raster input")
    if include_R4 is True: 
        raster[count] = np.array(ds4.GetRasterBand(1).ReadAsArray())
        count+=1
    
    ds5=gdal.Open(R5)
    if ds5 is None:
        print("ERROR: can't open raster input")
    if include_R5 is True: 
        raster[count] = np.array(ds5.GetRasterBand(1).ReadAsArray())
        count+=1
    
    ds6=gdal.Open(R6)
    if ds6 is None:
        print("ERROR: can't open raster input")
    if include_R6 is True: 
        raster[count] = np.array(ds6.GetRasterBand(1).ReadAsArray())
        count+=1
    
    ds7=gdal.Open(R7)
    if ds7 is None:
        print("ERROR: can't open raster input")
    if include_R7 is True: 
        raster[count] = np.array(ds7.GetRasterBand(1).ReadAsArray())
        count+=1
    
    ds8=gdal.Open(R8)
    if ds8 is None:
        print("ERROR: can't open raster input")
    if include_R8 is True: 
        raster[count] = np.array(ds8.GetRasterBand(1).ReadAsArray())
        count+=1
    
    ds9=gdal.Open(R9)
    if ds9 is None:
        print("ERROR: can't open raster input")
    if include_R9 is True: 
        raster[count] = np.array(ds9.GetRasterBand(1).ReadAsArray())
        count+=1
    
    ds10=gdal.Open(R10)
    if ds10 is None:
        print("ERROR: can't open raster input")
    if include_R10 is True: 
        raster[count] = np.array(ds10.GetRasterBand(1).ReadAsArray())
        count+=1
    return raster,x,y,ds1,count

def indexing():
    nune={}
    values={}
    LSI=np.zeros((y,x),dtype='float32')
    LSI[LSI==0]=-9999
    for i in range(count):
        #nune[i]=np.where(raster[i]==-9999)
        values=np.array([])
        values=np.where(raster[i]>-9999)
        LSI[values]=raster[i][values]
    return LSI
    del nune
    del values

def save():
    try:
        out_data = None
        # read in data from first band of input raster
        # create single-band float32 output raster
        driver = ds1.GetDriver()
        out_data = driver.Create(LSIout, x, y, 1, gdal.GDT_Float32)
        # set values below nodata threshold to nodata
        dem_data=np.array([])
        dem_data = LSI
        # write the data to output file
        out_band = out_data.GetRasterBand(1)
        out_band.WriteArray(dem_data, 0, 0)
        # flush data to disk, set the NoData value and calculate stats
        out_band.FlushCache()
        out_band.SetNoDataValue(-9999)
        # georeference the image and set the projection
        out_data.SetGeoTransform(ds1.GetGeoTransform())
        out_data.SetProjection(ds1.GetProjection())
    except:
        print('ops')

raster,x,y,ds1,count=importing()
LSI=indexing()
save()
del raster
del LSI




