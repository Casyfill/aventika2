#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import datetime
import sys
import os
# from glob import glob
# import os


def getLogger():


    logger = logging.getLogger('root')
    logger.setLevel(logging.INFO)

    path = os.getcwd()
    path = path.replace('code/', '')

    date = datetime.datetime.now().strftime('%Y_%m_%d__%H:%M')
    handler = logging.FileHandler(path + '/logs/%s_scraping.log' % date)
    handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    logger.addHandler(console)

    def exception_handler(type, value, tb):
    	logger.exception("Uncaught exception: {0}".format(str(value)))

#    sys.excepthook = exception_handler
    
    return logger


log_row_string = '{i}: row stored, results: office_id:{bid} |score: {s}'
log_pois_string = '{i}: Pois at the start of the loop: {n}'
