#!/usr/bin/env python
# -*- coding: utf-8 -*-
# from buffers import selfSubstract
import geopandas as gp
import pandas as pd
import numpy as np
import logging
from shapely.geometry import shape, mapping
LOGGER = logging.getLogger('root')


def get_overlay(buff, reg):
    '''transforms regions into set of non-covered
    elements. for each we get a centroid and assigned
    score

    Args:
        buff:buffer
        reg: regions

    Returns:
        points geodataframe
    '''
    z = gp.overlay(buff, reg, 'union')
    z = z[pd.notnull(z['reg_id'])]
    z = z[z.area > 2000]

    z['score'] = z['disabled'] * z.area / z['reg_area']
    z['area'] = z.area
    z['geometry'] = z.representative_point()
    z = z[z.intersects(buff.unary_union)]
    z['reg_id'] = z['reg_id'].astype(int).astype(
        str) + '_' + z.index.astype(str)

    return z[['reg_id','area','reg_area', 'geometry', 'score']]


def drop_poi(buff, poi, settings):
    '''drop pois outside of buffers'''
    n_pois = len(poi)
    z = buff.unary_union

    LOGGER.info('Unary_union created')
    poi = poi[poi.intersects(z)]
    LOGGER.info(
        'Dropped {} pois, as they are out of borders'.format(n_pois - len(poi)))

    return poi


def _bufferize(geoDF):
    geoDF['geometry'] = geoDF.buffer(0)
    return geoDF


def around(geom, p):
    geojson = mapping(geom)
    geojson['coordinates'] = np.round(np.array(geojson['coordinates']), p)
    return shape(geojson)


def prepare(buff, poi, reg, settings):
    '''optimize geometry for the iteration'''
    poi = drop_poi(buff, poi, settings)

    if settings["reg_geom"]:
        reg = _bufferize(reg)
        regs_overlayed = get_overlay(buff, reg)
        LOGGER.info('Created region overlay')
    else:
        regs_overlayed = None

    buff = _bufferize(buff)
    LOGGER.info('geometry bufferized')

    return buff, poi, regs_overlayed
