#####################################################
# Description: Create equidistant points on lines with distances of 1m
# Containing the X, Y and Z location
# Input are predefined lines, based on the data
# Basis input is the folder structure in Data pre[
# 'Area name' // 'DEMS' --> tiffs with the bed elevation data per date
# 'Area name' // 'Meta' --> metadata (describing the files in each tiff
# 'Area name' // 'lines.shp' --> shape file with the lines to create the points on
# 'Area name' // 'PointData.gdb' --> workspace folder to create the point data
# 'Area name' // 'PointCSVs' --> folder with the point and line data per date
#
# Author: LR Lokin (UTwente)
# Python version: 2.7.15
# Packages: arcpy, os, csv
# Licences: ArcGis, 3D Analyst
# Date: 2021-02-19
#####################################################

# Import system modules
import arcpy
from arcpy import env
from arcpy.sa import *

import os
import csv

import exceptions, sys, traceback

# Set folders, names and environment settings
workDir = r'c:\Users\LokinLR\Documents\01_PhD\02_Data\03_Scripts'
Area = 'MiddenWaal'

## n
baseFolder = os.path.join(workDir, Area)

MBESFolder = os.path.join(baseFolder, 'DEMS')
# CSVfolder = os.path.join(baseFolder, 'PointCSVs')
SHPfolder = os.path.join(baseFolder, 'PointSHPs')

linesFile = os.path.join(baseFolder,'Lines.shp')
workGDB = os.path.join(baseFolder,'PointData.gdb')
tiffs =  os.listdir(MBESFolder)

env.workspace = workGDB

# if not os.path.exists(CSVfolder):
#     os.mkdir(CSVfolder)

if not os.path.exists(SHPfolder):
    os.mkdir(SHPfolder)
fieldNames = [u'OBJECTID', u'LineID', u'POINT_X', u'POINT_Y', u'POINT_Z']

# Check out the neccesary extentions
arcpy.CheckOutExtension("3D")
# Create the points to pinn the z data on
# Execute GeneratePointsAlongLines by distance, only if the points do not exist already
if not arcpy.Exists('Points'):
    arcpy.GeneratePointsAlongLines_management(linesFile,'Points',
                                              'DISTANCE',Distance = '1 meters'
                                              )
    print 'Points generated'
else:
    print 'Points already exist'


for tiff in tiffs:
    if not tiff[-4:] == '.tif':
        continue
    datemin = tiff.split('_')[1]
    datemax = tiff.split('_')[2][:-4]

    pointsZ = 'Z_{}_{}'.format(datemin,datemax)
    print 'Surface information from file:\n {}'.format(tiff)

    if arcpy.Exists(pointsZ):
        print 'Surface information already added'
    else: # sample distance mag naar 50
        arcpy.InterpolateShape_3d(in_surface = os.path.join(MBESFolder, tiff),
                                  in_feature_class = 'Points',
                                  out_feature_class =  pointsZ,
                                  sample_distance = 50,
                                  z_factor = "1",
                                  method = "BILINEAR",
                                  vertices_only="DENSIFY",
                                  pyramid_level_resolution="0",
                                  preserve_features="PRESERVE")
        if arcpy.Describe(pointsZ).hasZ == True:
            print 'Added surface information'
        else:
            print 'Surface information was not added for {}'.format(pointsZ)
            break
    
##        arcpy.AddGeometryAttributes_management(Input_Features=pointsZ,
##                                               Geometry_Properties="POINT_X_Y_Z_M",
##                                               Length_Unit="", Area_Unit="",
##                                               Coordinate_System="PROJCS['RD_New',GEOGCS['GCS_Amersfoort',DATUM['D_Amersfoort',SPHEROID['Bessel_1841',6377397.155,299.1528128]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Double_Stereographic'],PARAMETER['False_Easting',155000.0],PARAMETER['False_Northing',463000.0],PARAMETER['Central_Meridian',5.38763888888889],PARAMETER['Scale_Factor',0.9999079],PARAMETER['Latitude_Of_Origin',52.15616055555555],UNIT['Meter',1.0]]")

    if os.path.exists(os.path.join(SHPfolder, '{}.shp'.format(pointsZ))):
        print 'Shapefile {} already exists'.format(pointsZ)
    else:
        print 'Create shapefile from {}'.format(pointsZ)   
        arcpy.FeatureClassToShapefile_conversion(pointsZ,SHPfolder)
    
##    csvOut = 'DEMdata_{}_{}.csv'.format(datemin,datemax)
##    if os.path.exists(os.path.join(CSVfolder,csvOut)):
##        '{} already exists'.format(csvOut)
##        continue
##    else:
##        with open(os.path.join(CSVfolder,csvOut),'wb') as csvFile:
##            writer = csv.writer(csvFile, delimiter = ',')
##            writer.writerow(fieldNames)
##            with arcpy.da.SearchCursor(pointsZ,fieldNames) as cursor:
##                for row in cursor:
##                    writer.writerow(row)
##            csvFile.close()
    print 'Created the following file:\n{}\n'.format(pointsZ)
##    
print('\n*****FINISHED*****\n')
    
