#!/usr/bin/env python
# -*- coding: utf-8 -*-
# from buffers import selfSubstract


def prepare(buff, poi, reg, settings):
    '''optimize geometry for the iteration'''

    n_pois = len(poi)
    poi = poi[poi.intersects(buff.unary_union)]
    settings['logger'].info(
        'Dropped {} pois, as they are out of borders'.format(len(poi) - n_pois))

    return buff, poi, reg
