#!/usr/bin/env python
# -*- coding: utf-8 -*-
# from buffers import selfSubstract


def prepare(buff, poi, reg):
    '''optimize geometry for the iteration'''

    poi = poi[poi.intersects(buff.unary_union)]
    reg_centroids = reg.centroid
    reg.loc[reg.type == 'foot', 'score'] *= .8

    return buff, poi, reg, reg_centroids
