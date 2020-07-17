# DuneDataAnalysis
This repository is to start working on the dune data analysis. Developed in order for the first workpackage within my PhD research on river dune development.

# Data Organisation
## Available data
The available data consist of two parts, the bed elevation data and the secondary data. Secondary data will help to do the analysis of the derived dunes
Available Bed elevation data:
- CoVadem data; LatLon position, Time and several columns. Reference system; WGS84, epsg4326
- RWS data; ascii/tif files, 1x1 gridded MBES data. Reference system; Amersfoort/RDnew, epsg28992
- RWS pointclouds; raw MBES data

Available secondary data:
- Water levels in time, at several locations along the Rhine and Waal
- Measured/derived discharges
- Sediment size information??
- Flow fields calculated with DelftFM??

## Scripts
Data organizing scripts are the scripts that prepare the data from CoVadem and RWS for the dune tracking algorithm. Such that these can be dealt with considering computer RAM etc.



# DuneTracking
DuneTracking tools available in papers:
- OpenATM, Gutierrez et al. (2018)
- BedTrackingTool


# dune analysis
