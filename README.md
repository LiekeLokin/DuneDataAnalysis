# DuneDataAnalysis
This repository contains the all code needed to do a dune analysis on the dunes of the Waal river.
The functions in duneAnalaysis are generic and can be applied on any bed elevation profile that contains dunes, given that the input parameters are set correctly. Input data must have equidistant points along the bed elevation profile.

The duneAnalysis_WaalNL performs the analysis on bed elevation profiles of the Waal River in the Netherlands. The data will be publisched upon acceptance of the paper written with these scripts (doi). RAW bed elevation data may be requested at Rijkswaterstaat (Ministry of Infrastructure and Watermanagement, the Netherlands). Discharge data at measuringstation Tiel, can be obtained from waterinfo.rws.nl.

The duneAnalysis functioans are developed with the following packages:
- numpy 1.21.4
- scipy 1.7.3
- wavelets @ git+https://github.com/LiekeLokin/wavelets@a213d7c307e0a6b5a40cc648d4e3f69c2e77c12b
