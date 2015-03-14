# -*- coding: utf-8 -*-
#General libraries
# import os
import math
# import csv
#Geospatial libraries
# import fiona
from shapely.geometry import mapping
#Clases
# import settings


def to_features(geoms, properties={}):
    features = []
    for polygon in geoms:
        f = {}
        f['geometry'] = mapping(polygon)
        f['properties'] = properties
        features.append(f)
    return features


def to_feature(geom, properties={}):
    feature = dict()
    feature['geometry'] = mapping(geom)
    feature['properties'] = properties
    return feature


def make_uso_id(uso_id, index):
    new_uso_id = None
    uso_id = float(uso_id)
    int_part = math.floor(uso_id)
    decimal_part = str(uso_id - int(uso_id))[2:]
    if decimal_part == "0":
        decimal_part = str(int(decimal_part) + index)
    else:
        decimal_part = decimal_part + str(index)
    # size = len(decimal_part)
    new_uso_id = str(int(int_part)) + "." + decimal_part
    return new_uso_id
