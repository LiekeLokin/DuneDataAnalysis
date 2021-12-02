# -*- coding: utf-8 -*-
"""
This file contains all necessary functions to perform the wavelet analysis based
Dune Analysis.

Requirements:
    - python 3.4+
    - numpy (developed with)
    - scipy (developed with)
    
    
    - wavelets, from https://github.com/aaren/wavelets, code based on 
        Torrence and Compo 1997.

@author: L.R. Lokin, l.r.lokin@utwente.nl
"""
import numpy as np

from scipy.interpolate import interpolate
from scipy.signal import find_peaks, correlate

import wavelets
from wavelets import WaveletAnalysis
from wavelets import Morlet

## nan fillers

def fillnan2D(array):
    '''
    interpolate nan within the data
    '''
    x = np.arange(0, array.shape[1])
    y = np.arange(0, array.shape[0]).T
    #mask invalid values
    array = np.ma.masked_invalid(array)
    xx, yy = np.meshgrid(x, y)
    #get only the valid values
    x1 = xx[~array.mask]
    y1 = yy[~array.mask]
    newarr = array[~array.mask].ravel()

    GD1 = interpolate.griddata((x1, y1), newarr,
                              (xx, yy),
                                 method='cubic')
    
    return(GD1)

def replaceNan(a):
    '''
    replace nan valeus at the end of a signal
    '''
    ind = np.where(~np.isnan(a))[0]
    first, last = ind[0], ind[-1]
    a[:first] = a[first]
    a[last + 1:] = a[last]
    return(a)


# dune Shape analysis

def findCrests(zFilt,Zrec,istart = 0):
    '''
    Find crests in the dune profile
    zFilt: Filtered bed elevation profile (ripples filtered out)
    Zrec: reconstructed bedprofile based on the wavelet spectrum, and the limits of the expected dunes
    istart: start index if not the whole profile is being analysed
    iend: end index if not the whole profile is being analysed
    '''
    
    recCr = find_peaks(Zrec)[0]
    allCr = find_peaks(zFilt, prominence = 0.1)[0]
    
#     print(16500/len(recCr), 16500/len(allCr))
    
    diffMatrix = np.repeat(allCr[:, np.newaxis], len(recCr), axis=1)
    if len(diffMatrix) == 0:
        Mcrests = []
    else:
#     print(np.argmin(abs(diffMatrix-recCr),axis = 0))
        Mcrests = allCr[np.unique(np.argmin(abs(diffMatrix-recCr), axis = 0))]+istart
    
    return(Mcrests)
    
def findTroughs(zFilt, Mcrests, istart = 0,iend = -1):
    '''
    Find the troughs between the crests
    zFilt: Filtered bed elevation profile (ripples filtered out)
    Mcrests: indices of the crest locations
    istart: start index if not the whole profile is being analysed
    iend: end index if not the whole profile is being analysed
    '''
    if iend == -1:
        iend = len(zFilt)
    
    Mtroughs = []
    
    if np.argmin(zFilt[istart:Mcrests[0]]) != 0:
        trough = istart+np.argmin(zFilt[istart:Mcrests[0]])
        Mtroughs = np.append(Mtroughs,int(trough))
    
    for i in np.arange(len(Mcrests)-1):
        trough = np.argmin(zFilt[Mcrests[i]:Mcrests[i+1]])+Mcrests[i]
#         print(Mcrests[i],trough)
        Mtroughs = np.append(Mtroughs, int(trough))
    
    if np.argmin(zFilt[Mcrests[-1]:iend]) != iend:
        trough = np.argmin(zFilt[Mcrests[-1]:iend])+Mcrests[-1]
        Mtroughs = np.append(Mtroughs, int(trough))
    
    return(Mtroughs)

def Wavelet2Dunes(Zbed, Zfilt, M, istart = 0, iend = -1, lowLim = 20, upLim = 300):
    '''
    Perform the actual dune analysis
    Zbed: is the 'raw' bed along one line
    Zfilt: is the filtered bed, where ripples are filtered out
    M: is the distance along the line in meters
    istart/iend: can be used to do the analysis over a section of the line
    lowLim/upLim: the lower and upper limits for reconstruction of the dune signal
        in the dune analysis.
    
    returns 
    Mcrests/Mtroughs:
        the indices of the crest and trough locations in Zbed and M
    rec: the reconstructed profile from the wavelet analysis
    wa: class containing the wavelet analysis resuts (see info of WaveletAnalysis)
    
    
    '''
    
    if iend == -1:
        iend = len(Zbed)
    if np.isnan(np.sum(Zbed)):
        Zbed = replaceNan(Zbed)
    wa = WaveletAnalysis(data = Zbed[istart:iend],
                                 time = M[istart:iend],
                                 dt = np.diff(M).mean(),
                                 wavelet = Morlet(),
                                 unbias = True,
                                 mask_coi = False)
    rec      = np.real(wa.reconstruction(scales = np.arange(lowLim,upLim)))

    Mcrests  = findCrests(Zfilt[istart:iend],rec, istart)
    if len(Mcrests) != 0:
        Mtroughs = findTroughs(Zfilt, Mcrests, istart,iend).astype(int)
    else:
        Mtroughs = []
    return(Mcrests,Mtroughs,rec,wa)

def duneHeightLengthRatio(signal, M, imax, imin):
    '''
    input
    signal: Filtered bed elevation without the ripples
    M: length along axis
    imax: crest locations
    imin: trough locations
    
    returns
    lengths: lenghts of all individual dunes in the profile
    heights: heights of all individual dunes in the profile
    lhratio: aspect ratio of all individual dunes in the profile
    leeSlope: in degrees
    
    Filter is needed,
    Determine dune height
    '''
    
    # return only the lengths and heigths that belong togheter 
    lengths = M[imin[1:]]-M[imin[:-1]]
    dM = np.diff(M).mean()
    if (imax[0]>imin[0]) & (imax[-1]>imin[-1]): # signal starts with trough, ends with crest:
        heights = signal[imax[:-1]]-signal[imin[1:]]
        
        leeSlope = []
        for iMax, iMin in zip(imax[:-1], imin[1:]):
            lee = signal[iMax:iMin]
            h16 = (signal[iMax]-signal[iMin])/6
            iLeemax = np.abs(lee - (lee[0]-h16)).argmin()
            iLeemin = np.abs(lee - (lee[-1]+h16)).argmin()
            Slee = (lee[iLeemax]-lee[iLeemin])/(dM*(iLeemin-iLeemax))
            leeSlope = np.append(leeSlope,(np.arctan(Slee)))
            
    elif (imax[0]>imin[0]) & (imax[-1]<imin[-1]): # signal starts with trough, ends with trough:
        heights = signal[imax]-signal[imin[1:]]
        
        leeSlope = []
        for iMax, iMin in zip(imax, imin[1:]):
            lee = signal[iMax:iMin]
            h16 = (signal[iMax]-signal[iMin])/6
            iLeemax = np.abs(lee - (lee[0]-h16)).argmin()
            iLeemin = np.abs(lee - (lee[-1]+h16)).argmin()      
            Slee = (lee[iLeemax]-lee[iLeemin])/(dM*(iLeemin-iLeemax))
            leeSlope = np.append(leeSlope,(np.arctan(Slee)))
            
    elif (imax[0]<imin[0]) & (imax[-1]<imin[-1]): # signal starts with crest, ends with trough:
        heights = signal[imax[1:]]-signal[imin[1:]]
        
        leeSlope = []
        for iMax, iMin in zip(imax, imin):
            lee = signal[iMax:iMin]
            h16 = (signal[iMax]-signal[iMin])/6
            iLeemax = np.abs(lee - (lee[0]-h16)).argmin()
            iLeemin = np.abs(lee - (lee[-1]+h16)).argmin()
            Slee = (lee[iLeemax]-lee[iLeemin])/(dM*(iLeemin-iLeemax))
            leeSlope = np.append(leeSlope,(np.arctan(Slee)))
        
    elif (imax[0]<imin[0]) & (imax[-1]>imin[-1]): # signal starts with crest, ends with crest:
        heights = signal[imax[1:-1]]-signal[imin[1:]]
        
        leeSlope = []
        for iMax, iMin in zip(imax[1:-1], imin[1:]):
            lee = signal[iMax:iMin]
            h16 = (signal[iMax]-signal[iMin])/6
            iLeemax = np.abs(lee - (lee[0]-h16)).argmin()
            iLeemin = np.abs(lee - (lee[-1]+h16)).argmin()
            Slee = (lee[iLeemax]-lee[iLeemin])/(dM*(iLeemin-iLeemax))
            leeSlope = np.append(leeSlope,(np.arctan(Slee)))
        
    else:
        print(imin,imax)
    # if dune heigth is smaller than 0 it is no dune and eliminate this one from the dataset
    lengths = lengths[np.where(heights>=0.0)]
    heights = heights[np.where(heights>=0.0)]
    leeSlope = leeSlope[np.where(heights>=0.0)]
    
    lengths = lengths[np.where(lengths<=300)]
    heights = heights[np.where(lengths<=300)]
    leeSlope = leeSlope[np.where(lengths<=300)]
    
    lhratio = heights/lengths
    
    return(lengths,heights,lhratio,leeSlope*180/np.pi)


## determining displacement between two measured profiles to derive the dune celerity
def lag_finder(y1, y2, sr, thresholdMax = 300, thresholdMin = 5):
    '''
    Find the lag between two signals
    input: 
        y1: signal at t1
        y2: signal at t2
        sr: distance between two consequetive points in the signal (dM)
        thresholdMax: max displacement of the dunes in one timestep (genrally order of magnitude as the dune length expected)
        thresholdMin: min displacement, to omit small cross correlations if the signals cannot be correlated due to large displacements
        
        plot: creat ea plot
    
    '''
    n = len(y1)
    corr = correlate(y2, y1, mode='same') / np.sqrt( correlate(y1, y1, mode='same')[int(n/2)] *  correlate(y2, y2, mode='same')[int(n/2)])
#     print(int(np.floor(n/2)))
    corr = corr[int(np.floor(n/2))+thresholdMin:int(np.floor(n/2))+thresholdMax]
    
    delay_arr = np.linspace(-0.5*n/sr, 0.5*n/sr, n)
    delay_arr = delay_arr[int(np.floor(n/2))+thresholdMin:int(np.floor(n/2))+thresholdMax]
    
    delay = delay_arr[np.argmax(corr)]
    corrmax = np.max(corr)

    return(delay,corrmax)

