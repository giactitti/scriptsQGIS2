##Sampler=name
##Inventory=vector
##TrainPercentage=number
##OutTrain=output vector
##OutValid=output vector



#coding=utf-8
import numpy as np
from osgeo import gdal,osr,ogr
import sys
import math
import csv
from qgis.core import QgsMessageLog
import os
from scipy.ndimage import generic_filter
import random

def importing():
    driverd = ogr.GetDriverByName('ESRI Shapefile')
    ds9 = driverd.Open(Inventory,0)
    layer = ds9.GetLayer()
    ref = layer.GetSpatialRef()
    for feature in layer:
        geom = feature.GetGeometryRef()
        xy=np.array([geom.GetX(),geom.GetY()])
        try:
            XY=np.vstack((XY,xy))
        except:
            XY=xy
    return XY,ref

def sampler():
    l=len(XY)
    vec=np.arange(l)
    tt=np.ceil((TrainPercentage/100.)*l).astype(int)
    t=np.asarray(random.sample(range(0, l), tt))
    vec[t]=-9999
    v=vec[vec>-9999]
    return v,t

def saveV():
    # set up the shapefile driver
    driver = ogr.GetDriverByName("ESRI Shapefile")
    # Remove output shapefile if it already exists
    if os.path.exists(OutValid):
        driver.DeleteDataSource(OutValid)
    # create the data source
    ds=driver.CreateDataSource(OutValid)
    # create the layer
    layer = ds.CreateLayer("Validation", ref, ogr.wkbPoint)
    # Add the fields we're interested in
    field_name = ogr.FieldDefn("id", ogr.OFTInteger)
    field_name.SetWidth(100)
    layer.CreateField(field_name)
    # Process the text file and add the attributes and features to the shapefile
    for i in range(len(v)):
        # create the feature
        feature = ogr.Feature(layer.GetLayerDefn())
        # Set the attributes using the values from the delimited text file
        feature.SetField("id", i)
        # create the WKT for the feature using Python string formatting
        wkt = "POINT(%f %f)" % (float(XY[v[i],0]) , float(XY[v[i],1]))
        # Create the point from the Well Known Txt
        point = ogr.CreateGeometryFromWkt(wkt)
        # Set the feature geometry using the point
        feature.SetGeometry(point)
        # Create the feature in the layer (shapefile)
        layer.CreateFeature(feature)
        # Dereference the feature
        feature = None
    # Save and close the data source
    ds = None
    
def saveT():
    # set up the shapefile driver
    driver = ogr.GetDriverByName("ESRI Shapefile")
    # Remove output shapefile if it already exists
    if os.path.exists(OutTrain):
        driver.DeleteDataSource(OutTrain)
    # create the data source
    ds=driver.CreateDataSource(OutTrain)
    # create the layer
    layer = ds.CreateLayer("Training", ref, ogr.wkbPoint)
    # Add the fields we're interested in
    field_name = ogr.FieldDefn("id", ogr.OFTInteger)
    field_name.SetWidth(100)
    layer.CreateField(field_name)
    # Process the text file and add the attributes and features to the shapefile
    for i in range(len(t)):
        # create the feature
        feature = ogr.Feature(layer.GetLayerDefn())
        # Set the attributes using the values from the delimited text file
        feature.SetField("id", i)
        # create the WKT for the feature using Python string formatting
        wkt = "POINT(%f %f)" % (float(XY[t[i],0]) , float(XY[t[i],1]))
        # Create the point from the Well Known Txt
        point = ogr.CreateGeometryFromWkt(wkt)
        # Set the feature geometry using the point
        feature.SetGeometry(point)
        # Create the feature in the layer (shapefile)
        layer.CreateFeature(feature)
        # Dereference the feature
        feature = None
    # Save and close the data source
    ds = None

XY,ref=importing()
v,t=sampler()
saveV()
saveT()