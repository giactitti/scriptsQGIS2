##InventoryRaster=name
##InventoryShp=vector
##DEM=raster
##output=output raster

import numpy as np
from osgeo import gdal
from osgeo import ogr
import sys
import math
import csv

def rasterization():
    driver = ogr.GetDriverByName('ESRI Shapefile')
    ds = driver.Open(InventoryShp,0)
    if ds is None:
        print("ERROR: can't open raster input")
    layer = ds.GetLayer()
    for feature in layer:
        geom = feature.GetGeometryRef()
        xy=np.array([geom.GetX(),geom.GetY()])
        try:
            XY=np.vstack((XY,xy))
        except:
            XY=xy
    return XY
    
def getcrs():
    dem = gdal.Open(DEM)
    if dem is None:
        print("ERROR: can't open raster input")
    matrix = np.array(dem.GetRasterBand(1).ReadAsArray())
    cols = dem.RasterXSize
    rows = dem.RasterYSize
    gt= dem.GetGeoTransform()
    minx = gt[0]#lower left vertex
    #miny = gt[3] - rows*math.fabs(gt[5])#upper left vertex
    miny = gt[3]
    size=np.array([abs(gt[1]),abs(gt[5])])
    OS=np.array([minx,miny])
    print OS
    return OS,size,dem,cols,rows,matrix
    
def transformation():
    NumPxl=(np.ceil(abs((XY-OS)/size)-1))#from 0 first cell
    NumPxl[NumPxl==-1.]=0
    driver = dem.GetDriver()
    out_data = driver.Create(output, cols, rows, 1, gdal.GDT_Float32)
    values=np.zeros((rows,cols),dtype=float)
    if out_data is None:
        print('Could not create output file')
    # set values below nodata threshold to nodata
    for i in range(len(NumPxl)):
        values[NumPxl[i,1].astype(int),NumPxl[i,0].astype(int)]=1.
        #print NumPxl[i,0].astype(int),NumPxl[i,1].astype(int)
    dem_data = values
    idx=np.where(np.isnan(matrix))
    values[idx]=-9999
    # write the data to output file
    out_band = out_data.GetRasterBand(1)
    out_band.WriteArray(dem_data, 0, 0)
    # flush data to disk, set the NoData value and calculate stats
    out_band.FlushCache()
    out_band.SetNoDataValue(-9999)
    # georeference the image and set the projection
    out_data.SetGeoTransform(dem.GetGeoTransform())
    out_data.SetProjection(dem.GetProjection())

XY=rasterization()
OS,size,dem,cols,rows,matrix=getcrs()
transformation()