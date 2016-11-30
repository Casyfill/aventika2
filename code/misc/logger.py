#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import datetime
# from glob import glob
# import os


def getLogger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    date = datetime.datetime.now().strftime('%Y_%m_%d')
    handler = logging.FileHandler('%s_scraping.log' % date)
    handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    logger.addHandler(console)

    return logger


log_row_string = '{i}: row stored, results: office_id:{bid} |score: {s}'
log_pois_string = '{i}: Pois at the start of the loop: {n}'
