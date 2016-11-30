#!/usr/bin/env python
# -*- coding: utf-8 -*-
# from buffers import selfSubstract

#####################################################   Preparation

def prepare(buff, poi, reg):
    '''optimize geometry for the iteration'''
    
    #l1 = len(poi)
    #poi = poi[poi.intersects(buff['geometry'].unary_union)]
    #print('Dropped {} POIS outside of the buffer zone'.format(l1 - len(poi)))
          
    # buff = selfSubstract(buff)
    reg_centroids = reg.centroid
    reg.loc[reg.type=='foot','score']*=.8
    
    return buff, poi, reg, reg_centroids