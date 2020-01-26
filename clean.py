##Clean=name
##Slope=raster
##Inventory=vector
##Out=output vector
##Extension=extent
##BufferRadiousInPxl=number
##minSlopeAcceptable=number



#coding=utf-8
import numpy as np
from osgeo import gdal,osr,ogr
import sys
import math
import csv
from qgis.core import QgsMessageLog
import os
from scipy.ndimage import generic_filter

limits=np.fromstring(Extension, dtype=float, sep=',')
xmin=limits[0]
xmax=limits[1]
ymin=limits[2]
ymax=limits[3]

def importing():
    raster={}
    ds=gdal.Open(Slope)
    xc = ds.RasterXSize
    yc = ds.RasterYSize
    geot=ds.GetGeoTransform()
    newXNumPxl=np.round(abs(xmax-xmin)/(abs(geot[1]))).astype(int)
    newYNumPxl=np.round(abs(ymax-ymin)/(abs(geot[5]))).astype(int)
    try:
        os.system('gdal_translate -of GTiff -ot Float32 -strict -outsize ' + str(newXNumPxl) +' '+ str(newYNumPxl) +' -projwin ' +str(xmin)+' '+str(ymax)+' '+ str(xmax) + ' ' + str(ymin) +' -co COMPRESS=DEFLATE -co PREDICTOR=1 -co ZLEVEL=6 ' + Slope +' '+ '/tmp/sizedslopexxx.tif')
    except:
        raise ValueError  # Failure to save sized cause, see 'WoE' Log Messages Panel
    del ds
    ds1=gdal.Open('/tmp/sizedslopexxx.tif')
    if ds1 is None:
        print("ERROR: can't open raster input")
    nodata=ds1.GetRasterBand(1).GetNoDataValue()
    raster[0] = np.array(ds1.GetRasterBand(1).ReadAsArray())
    raster[0][raster[0]==nodata]=-9999
    x = ds1.RasterXSize
    y = ds1.RasterYSize
    driverd = ogr.GetDriverByName('ESRI Shapefile')
    ds9 = driverd.Open(Inventory,0)
    layer = ds9.GetLayer()
    for feature in layer:
        geom = feature.GetGeometryRef()
        xy=np.array([geom.GetX(),geom.GetY()])
        try:
            XY=np.vstack((XY,xy))
        except:
            XY=xy
    #print XY
    #print len(XY)
    gtdem= ds1.GetGeoTransform()
    size=np.array([abs(gtdem[1]),abs(gtdem[5])])
    OS=np.array([gtdem[0],gtdem[3]])
    #print OS
    NumPxl=(np.ceil((abs(XY-OS)/size)-1))#from 0 first cell
    NumPxl[NumPxl==-1.]=0
    #driver = ds1.GetDriver()
    #out_data = driver.Create('/tmp/inventorynxn.tif', x, y, 1, gdal.GDT_Float32)
    values=np.zeros((y,x), dtype='Int16')
    #if out_data is None:
    #    raise ValueError # Could not create output file, see 'WoE' Log Messages Panel
    #    # set values below nodata threshold to nodata
    #values[NumPxl[i,1].astype(int),NumPxl[i,0].astype(int)]=1
    #print len(NumPxl)
    for i in range(len(NumPxl)):
        if XY[i,1]<ymax and XY[i,1]>ymin and XY[i,0]<xmax and XY[i,0]>xmin:
            values[NumPxl[i,1].astype(int),NumPxl[i,0].astype(int)]=1
    raster[1]=values
    return raster,x,y,ds1,XY
    
    
def indexing():
    ggg=np.array([])
    ggg=raster[0].astype('float32')
    #nann=float('nan')
    #ggg[(ggg==-9999)]=nann
    R=np.array([])
    R=raster[1].astype('Int16')
    #R[(R==-9999)]=None
    R[(R==0)]=-9999
    #idx=np.where(raster[1]==1)
    #row,col=np.shape(ggg)
    #print row,col
    #print idx[0,:]
    #print ggg[idx[0,:]]
    numbb=BufferRadiousInPxl*2+1
    g = generic_filter(ggg, np.nanmax, size=(numbb,numbb))
    #oout=np.zeros((y,x),dtype='Int16')
    #v=g[idx]
    #print idx
    #for i in range(len(idx)):
    #    if g[idx[i]]>0:
    #        oout[idx[i]]=1
    #oout[(g[idx]>0)]=1
    oout=np.array([])
    oout=R*g
    oout[(raster[0]==-9999)]=-9999
    oout[(raster[1]==0)]=-9999
    oout[(oout<minSlopeAcceptable)]=-9999
    oout[oout>=minSlopeAcceptable]=1
    g=None
    ggg==np.array([])
    return oout

def vector():
    row,col=np.where(oout==1)
    geo=ds1.GetGeoTransform()
    xsize=geo[1]
    ysize=geo[5]
    OOx=geo[0]
    OOy=geo[3]
    #xycoord=np.zeros((len(col),2))
    XYcoord=np.array([0,0])
    for i in range(len(col)):
        xmin=OOx+(xsize*col[i])
        xmax=OOx+(xsize*col[i])+(xsize)
        ymax=OOy+(ysize*row[i])
        ymin=OOy+(ysize*row[i])+(ysize)
        for ii in range(len(XY)):
            if (XY[ii,0]>=xmin and XY[ii,0]<=xmax and XY[ii,1]>=ymin and XY[ii,1]<=ymax):
                XYcoord=np.vstack((XYcoord,XY[ii,:]))
        #xycoord[i,:]=np.array([OOx+(xsize*col[i])+(xsize/2),OOy+(ysize*row[i])+(ysize/2)])
        #rowXY,colXY=np.where((XY[:,0]>=xmin)&(XY[:,0]<=xmax)&(XY[:,1]>=ymin)&(XY[:,1]<=ymax))
    print(XYcoord)
    XYcoord=XYcoord[1:,:]
    return XYcoord

def saveV():
    # set up the shapefile driver
    driver = ogr.GetDriverByName("ESRI Shapefile")
    # Remove output shapefile if it already exists
    if os.path.exists(Out):
        driver.DeleteDataSource(Out)
    # create the data source
    ds=driver.CreateDataSource(Out)
    #print data_source
    # create the spatial reference, WGS84
    #srs = osr.SpatialReference().ImportFromEPSG(epsg)
#    epsg = int(osr.SpatialReference(wkt=ds1.GetProjection()).GetAttrValue('AUTHORITY',1))
#    print epsg
#    #srs.ImportFromEPSG(epsg)
#    srs = osr.SpatialReference()
#    srs.ImportFromEPSG(epsg)
#    print srs
#    print epsg
    srs=osr.SpatialReference(wkt = ds1.GetProjection())
    # create the layer
    layer = ds.CreateLayer("inventory_cleaned", srs, ogr.wkbPoint)
    # Add the fields we're interested in
    field_name = ogr.FieldDefn("id", ogr.OFTInteger)
    field_name.SetWidth(100)
    layer.CreateField(field_name)
    # Process the text file and add the attributes and features to the shapefile
    for i in range(len(XYcoord)):
        # create the feature
        feature = ogr.Feature(layer.GetLayerDefn())
        # Set the attributes using the values from the delimited text file
        feature.SetField("id", i)
        # create the WKT for the feature using Python string formatting
        wkt = "POINT(%f %f)" % (float(XYcoord[i,0]) , float(XYcoord[i,1]))
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

    

#def save():
# try:
#        out_data = None
#        # read in data from first band of input raster
#        # create single-band float32 output raster
#        driver = ds1.GetDriver()
#        out_data = driver.Create(Outt, x, y, 1, gdal.GDT_Float32)
#        # set values below nodata threshold to nodata
#        dem_data=np.array([])
#        dem_data = oout
#        # write the data to output file
#        out_band = out_data.GetRasterBand(1)
#        out_band.WriteArray(dem_data, 0, 0)
#        # flush data to disk, set the NoData value and calculate stats
#        out_band.FlushCache()
#        out_band.SetNoDataValue(-9999)
#        # georeference the image and set the projection
#        out_data.SetGeoTransform(ds1.GetGeoTransform())
#        out_data.SetProjection(ds1.GetProjection())
#    except:
#        print('ops')

#values,raster,x,y,ds1=importing()
#del values
#oout=indexing()
#save()
#del raster
#del oout
raster,x,y,ds1,XY=importing()
oout=indexing()
#save()
XYcoord=vector()
del oout
saveV()
del raster