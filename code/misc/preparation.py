#!/usr/bin/env python
# -*- coding: utf-8 -*-
# from buffers import selfSubstract


def prepare(buff, poi, reg, settings):
    '''optimize geometry for the iteration'''

    n_pois = len(poi)
    z = buff.unary_union
    settings['logger'].info('Unary_union created')
    poi = poi[poi.intersects(z)]
    settings['logger'].info(
        'Dropped {} pois, as they are out of borders'.format(n_pois - len(poi)))

    return buff, poi, reg
