#!/usr/bin/env python
# -*- coding: utf-8 -*-
# from buffers import selfSubstract
import geopandas as gp
import pandas as pd


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
    z['score'] = z['disabled'] * z.area / z['reg_area']
    z['geometry'] = z.centroid
    return z[['reg_id', 'geometry', 'score']]


def prepare(buff, poi, reg, settings):
    '''optimize geometry for the iteration'''

    n_pois = len(poi)
    z = buff.unary_union
    settings['logger'].info('Unary_union created')
    poi = poi[poi.intersects(z)]
    settings['logger'].info(
        'Dropped {} pois, as they are out of borders'.format(n_pois - len(poi)))

    reg['geometry'] = reg.buffer(0)
    buff['geometry'] = buff.buffer(0)
    settings['logger'].info('geometry bufferized')

    regs_overlayed = get_overlay(buff, reg)
    settings['logger'].info(
        'Created region overlay'.format(n_pois - len(poi)))

    return buff, poi, regs_overlayed
