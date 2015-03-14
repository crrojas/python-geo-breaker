#!/usr/bin/python
# -*- coding: utf-8 -*-
import math
from random import choice
# Geospatial libraries
#import fiona
from shapely.geometry import mapping, shape
from shapely.ops import unary_union
# Clases
import settings
import utils
from shape import *
import voro
import copy


def contour(usos, context):
    """Retorna un feature que representa el contour del problema"""
    features = usos.get_features()
    geoms = []
    for f in features:
        if f['properties']['TIPOUSO'] in context.haverstable:
            geoms.append(shape(f['geometry']))

    geom_contour = unary_union(geoms)
    contour_parts = []
    for gc in geom_contour:
        contour = {}
        contour['geometry'] = mapping(gc)
        contour['properties'] = {'TIPO': 'CONTOUR'}
        contour_parts.append(contour)
    return contour_parts


def rivers_slice(usos, rivers):
    """El shape de usos ya incluye esta información"""
    pass


def roads_slice(usos, roads):
    """El shape de usos ya incluye esta información"""
    pass


def geo(usos_shape, slope_shape, context, file_name=None, folder=None):
    """Se agrupan las pendientes en torres y skhu
    Por cada uso se genera una intersección"""
    geo_features = []
    slopes = slope_shape.get_features()

    # grappler = [] # Por qué no se considera?
    skhu = []
    tower = []
    #properties = slopes[0]['properties']
    for fs in slopes:
        slope_geom = shape(fs['geometry'])
        slope_code = int(fs['properties']['SLOPE_CODE']) -\
            context.slope_interval  # Parametrizar esto!!
        # if slope_code <= settings.max_equi_slope['GRAPPLER']
        #     grappler.append(slope_geom)
        if slope_code <= context.max_equi_slope['SKHU']:
            skhu.append(slope_geom)
        elif slope_code >= context.min_equi_slope['TORR'] and\
                slope_code <= context.max_equi_slope['TORR']:
            tower.append(slope_geom)
        else:
            print "La pendiente no corresponde con SKHU o TORR"
    # Superficie cosechada por huinches y grapplers
    skhu_surface = unary_union(skhu)
    # print 'skhu_surface', skhu_surface.geom_type, len(skhu_surface)
    # Superficie cosechada por torres
    tower_surface = unary_union(tower)
    # print 'tower_surface', tower_surface.geom_type, len(tower_surface)

    file_name = file_name if file_name is not None else "geo"

    context.usos_schema['properties']['EQUIPO'] = 'str:4'
    print "temp{0}{1}{2}{3}.{4}".format(os.sep, folder, os.sep, file_name, "shp")
    shape_usos_generados = Shape(
        "temp{0}{1}{2}{3}.{4}".format(os.sep, folder, os.sep, file_name, "shp"),
        context.usos_schema, True)

    usos = usos_shape.get_features()

    index = 0
    for uso in usos:
        if uso['properties']['TIPOUSO'] in context.haverstable:
            uso_geom = shape(uso['geometry'])
            skhu_slope_uso = uso_geom.intersection(skhu_surface)
            tower_slope_uso = uso_geom.intersection(tower_surface)

            # print skhu_slope_uso.geom_type, tower_slope_uso.geom_type

            # Eliminamos los polígonos de la superficie de skhu
            # que son muy pequeños
            significant_skhu = []
            if skhu_slope_uso.geom_type == "MultiPolygon":
                for polygon in skhu_slope_uso:
                    if polygon.area >= context.min_surface:
                        significant_skhu.append(polygon)
                    else:
                        tower_slope_uso = tower_slope_uso.union(polygon)
            elif skhu_slope_uso.geom_type == "Polygon":
                if skhu_slope_uso.area >= context.min_surface:
                    significant_skhu.append(skhu_slope_uso)
                else:
                    tower_slope_uso = tower_slope_uso.union(skhu_slope_uso)

            skhu_slope_uso = unary_union(significant_skhu)
            # Eliminamos los polígonos de la superficie de torre
            # que son muy pequeños
            significant_tower = []
            if tower_slope_uso.geom_type == "MultiPolygon":
                for polygon in tower_slope_uso:
                    if polygon.area >= context.min_surface:
                        significant_tower.append(polygon)
                    else:
                        skhu_slope_uso = skhu_slope_uso.union(polygon)
            elif tower_slope_uso.geom_type == "Polygon":
                if tower_slope_uso.area >= context.min_surface:
                    significant_tower.append(tower_slope_uso)
                else:
                    skhu_slope_uso = skhu_slope_uso.union(tower_slope_uso)

            tower_slope_uso = unary_union(significant_tower)

            # if skhu_slope_uso.area >= settings.min_surface:
            if skhu_slope_uso.geom_type in\
                    ["MultiPolygon", "GeometryCollection"]:
                for polygon in skhu_slope_uso:
                    skhu_feature = {}
                    skhu_feature['geometry'] = mapping(polygon)
                    skhu_feature['properties'] = uso['properties'].copy()
                    skhu_feature['properties']['AREA'] = polygon.area
                    skhu_feature['properties']['PERIMETER'] = polygon.length
                    skhu_feature['properties']['EQUIPO'] = 'SKU'
                    skhu_feature['properties']['USOS_ID'] =\
                        utils.make_uso_id(
                            skhu_feature['properties']['USOS_ID'], index)
                    geo_features.append(skhu_feature)
                    shape_usos_generados.add_features([skhu_feature])
                    index += 1
            elif skhu_slope_uso.geom_type == "Polygon":
                skhu_feature = {}
                skhu_feature['geometry'] = mapping(skhu_slope_uso)
                skhu_feature['properties'] = uso['properties'].copy()
                skhu_feature['properties']['AREA'] = skhu_slope_uso.area
                skhu_feature['properties']['PERIMETER'] = skhu_slope_uso.length
                skhu_feature['properties']['EQUIPO'] = 'SKU'
                skhu_feature['properties']['USOS_ID'] =\
                    utils.make_uso_id(
                        skhu_feature['properties']['USOS_ID'], index)
                geo_features.append(skhu_feature)
                shape_usos_generados.add_features([skhu_feature])
                index += 1
            else:
                print skhu_slope_uso.geom_type

            # if tower_slope_uso.area >= settings.min_surface:
            if tower_slope_uso.geom_type in\
                    ["MultiPolygon", "GeometryCollection"]:
                for polygon in tower_slope_uso:
                    tower_feature = {}
                    tower_feature['geometry'] = mapping(polygon)
                    tower_feature['properties'] = uso['properties'].copy()
                    tower_feature['properties']['AREA'] = polygon.area
                    tower_feature['properties']['PERIMETER'] = polygon.length
                    tower_feature['properties']['EQUIPO'] = 'TORR'
                    tower_feature['properties']['USOS_ID'] =\
                        utils.make_uso_id(
                            tower_feature['properties']['USOS_ID'], index)
                    geo_features.append(tower_feature)
                    shape_usos_generados.add_features([tower_feature])
                    index = index + 1
            elif tower_slope_uso.geom_type == "Polygon":
                tower_feature = {}
                tower_feature['geometry'] = mapping(tower_slope_uso)
                tower_feature['properties'] = uso['properties'].copy()
                tower_feature['properties']['AREA'] = tower_slope_uso.area
                tower_feature['properties']['PERIMETER'] =\
                    tower_slope_uso.length
                tower_feature['properties']['EQUIPO'] = 'TORR'
                tower_feature['properties']['USOS_ID'] =\
                    utils.make_uso_id(
                        tower_feature['properties']['USOS_ID'], index)
                geo_features.append(tower_feature)
                shape_usos_generados.add_features([tower_feature])
                index += 1
            else:
                print tower_slope_uso.geom_type

    return geo_features


def size(usos, courts_shape, roads_shape, max_size, context, file_name, folder):

    features = []
    final = Shape(
        "temp" + os.sep + folder + os.sep + file_name + ".shp", context.usos_schema, True)
    for uso in usos:
        print "Aplicando Voronoi:", uso['properties']['USOS_ID']
        geom = shape(uso['geometry'])
        if geom.area > max_size:
            new_features = voro.voronoi_tessellation(
                uso, courts_shape, roads_shape, max_size)
            if new_features is None:
                print "Error None Type: ", uso['properties']['USOS_ID']
            else:
                features.extend(new_features)
        else:
            features.append(uso)

    final.add_features(features)
    return features


def integrate(features, maxsize, context, file_name, folder):

    shape_file = Shape(
        "temp" + os.sep + folder + os.sep+ file_name + ".shp", context.usos_schema, True)
    minsize = 0.7
    for f1 in features:
        geom1 = shape(f1['geometry'])
        if (geom1.area / maxsize) <= minsize:
            # print "integrate", f['properties']['USOS_ID'], geom1.area
            new_feature = merge(f1, features, maxsize)
            features.extend(new_feature)
        else:
            #new_f1 = copy.deepcopy(f1)
            # final_features.append(f1)
            pass

    # Por si acaso
    for f1 in features:
        geom1 = shape(f1['geometry'])
        if (geom1.area / maxsize) <= minsize:
            # print "integrate", f['properties']['USOS_ID'], geom1.area
            new_feature = merge(f1, features, maxsize)
            features.extend(new_feature)
        else:
            #new_f1 = copy.deepcopy(f1)
            # final_features.append(f1)
            pass

    for f1 in features:
        geom1 = shape(f1['geometry'])
        # remove garbage
        min_size = 100
        if geom1.area < min_size:
            print "Remove garbage"
            # print "integrate", f['properties']['USOS_ID'], geom1.area
            #new_feature = merge(f1, features, maxsize)
            features.remove(f1)

    shape_file.add_features(features)
    return features, shape_file


def merge(small, features, maxsize):
    accum_size = shape(small['geometry']).area
    # neighbors = sorted(get_neighbors(small, features),
    #     key=lambda f: shape(f['geometry']).area)

    neighbors = get_neighbors(small, features)

    try:
        features.remove(small)
    except:
        pass

    solution = [small]
    USO = small['properties']['TIPOUSO']
    EQUIPO = small['properties']['EQUIPO']
    for n in neighbors:
        U = n['properties']['TIPOUSO']
        E = n['properties']['EQUIPO']
        #Ḿezclar solo si coincide tipo de uso y pendiente
        if (shape(n['geometry']).area + accum_size <= maxsize)\
                and (U == USO) and (E == EQUIPO):

            accum_size += shape(n['geometry']).area
            solution.append(n)
            neighbors.remove(n)
            try:
                features.remove(n)
            except:
                pass
            neighbors.extend(get_neighbors(n, features, solution))

    merge_features = []
    if len(solution) >= 1:
        father = higher(solution)
        polygon = union(solution)
        if polygon.geom_type == "Polygon":
            f = {}
            f['geometry'] = mapping(polygon)
            f['properties'] = father['properties'].copy()
            f['properties'][u'AREA'] = polygon.area
            f['properties'][u'PERIMETER'] = polygon.length
            f['properties'][u'USOS_ID'] = father['properties']['USOS_ID']
            merge_features.append(f)
        elif polygon.geom_type in ["MultiPolygon", "GeometryCollection"]:
            for part in polygon:
                f = {}
                f['properties'] = {}
                f['geometry'] = mapping(part)
                f['properties'] = father['properties'].copy()
                f['properties'][u'AREA'] = part.area
                f['properties'][u'PERIMETER'] = polygon.length
                f['properties'][u'USOS_ID'] = father['properties']['USOS_ID']
                merge_features.append(f)
        else:
            print polygon.geom_type

    else:
        pass

    return merge_features


def higher(features):
    feature = features[0]
    first_geom = shape(feature['geometry'])
    higher = first_geom.area
    for f in features:
        geom = shape(f['geometry'])
        if geom.area >= higher:
            feature = f
            higher = geom.area
    return feature


def union(features):
    geoms = []
    for f in features:
        g = shape(f['geometry'])
        geoms.append(g)
    return unary_union(geoms)


def get_neighbors(feat, all_features, excludes=[]):
    neighbors = []
    geom1 = shape(feat['geometry'])
    # bgeom1 = geom1.buffer(10)
    for f in all_features:
        geom2 = shape(f['geometry'])
        if geom1 is not geom2 and geom2 not in map(
                lambda f: shape(f['geometry']), excludes):
            # print bgeom1.touches(geom2), bgeom1.crosses(geom2)
            if geom1.touches(geom2):
                neighbors.append(f)
    return neighbors


def tessellator(name, sizes, usos, slope, roads, courts, rivers=None):
    hectarea = 10000
    for maxsize in sizes:
        context = settings.Context(usos.schema.copy())
        geo_usos = geo(
            usos, slope, context, "geo_{0}_{1}".
            format(maxsize, name),
            name)
        print "geo finished"
        features = size(
            geo_usos, courts, roads, maxsize * hectarea,
            context, "voro_{0}_{1}".format(maxsize, name),
            name)
        print "access finished"
        final_name = "merge_{0}_{1}".format(maxsize, name)
        feats, final_solution = integrate(
            features, maxsize * hectarea, context, "merge_{0}_{1}".
            format(maxsize, name),
            name)
        print "integration finished"
        final_solution.neighbors_matrix(
            file_name="temp" + os.sep + name + os.sep + final_name + "_matrix.csv")


if __name__ == "__main__":

    import time

    sizes = [5, 10, 15, 20]

    start = time.time()
    usos = Shape("layers/elena_la1/usos.shp")
    slope = Shape("layers/elena_la1/pendi.shp")
    roads = Shape("layers/elena_la1/caminos.shp")
    courts = Shape("layers/elena_la1/canchas.shp")
    rivers = Shape("layers/elena_la1/buffer_hidro.shp")
    tessellator('elena_la1', sizes, usos, slope, roads, courts, rivers)
    end = time.time()
    print 'elena_la1: ', end - start

    # start = time.time()
    # usos = Shape("layers/sta_carla/usos.shp")
    # slope = Shape("layers/sta_carla/pendi.shp")
    # roads = Shape("layers/sta_carla/caminos.shp")
    # courts = Shape("layers/sta_carla/canchas.shp")
    # rivers = Shape("layers/sta_carla/hidro.shp")
    # tessellator('sta_carla', sizes, usos, slope, roads, courts, rivers)
    # end = time.time()
    # print 'sta_carla: ', end - start

    # usos = Shape("layers/san_ramon/usos.shp")
    # slope = Shape("layers/san_ramon/pendi.shp")
    # roads = Shape("layers/san_ramon/caminos.shp")
    # courts = Shape("layers/san_ramon/canchas.shp")
    # rivers = Shape("layers/san_ramon/hidro.shp")
    # tessellator('san_ramon', sizes, usos, slope, roads, courts, rivers)
    # print 'san_ramon'

    # usos = Shape("layers/san_ramon_sur/usos.shp")
    # slope = Shape("layers/san_ramon_sur/pendi.shp")
    # roads = Shape("layers/san_ramon_sur/caminos.shp")
    # courts = Shape("layers/san_ramon_sur/canchas.shp")
    # rivers = Shape("layers/san_ramon_sur/hidro.shp")
    # tessellator('san_ramon_sur', sizes, usos, slope, roads, courts, rivers)
    # print 'san_ramon_sur'

    # usos = Shape("layers/collico_2/usos.shp")
    # slope = Shape("layers/collico_2/pendi.shp")
    # roads = Shape("layers/collico_2/caminos.shp")
    # courts = Shape("layers/collico_2/canchas.shp")
    # rivers = Shape("layers/collico_2/hidro.shp")
    # tessellator('collico_2', sizes, usos, slope, roads, courts, rivers)
    # print 'collico_2'

    # usos = Shape("layers/quilantos/31022/usos.shp")
    # slope = Shape("layers/quilantos/31022/pendi.shp")
    # roads = Shape("layers/quilantos/31022/caminos.shp")
    # courts = Shape("layers/quilantos/31022/canchas.shp")
    # rivers = Shape("layers/quilantos/31022/hidro.shp")
    # tessellator('quilantos_31022', sizes, usos, slope, roads, courts)
    # print 'quilantos_31022'

    # usos = Shape("layers/quilantos/31023/usos.shp")
    # slope = Shape("layers/quilantos/31023/pendi.shp")
    # roads = Shape("layers/quilantos/31023/caminos.shp")
    # courts = Shape("layers/quilantos/31023/canchas.shp")
    # rivers = Shape("layers/quilantos/31023/hidro.shp")
    # tessellator('quilantos_31023', sizes, usos, slope, roads, courts)
    # print 'quilantos_31023'

    # usos = Shape("layers/quilantos/31024/usos.shp")
    # slope = Shape("layers/quilantos/31024/pendi.shp")
    # roads = Shape("layers/quilantos/31024/caminos.shp")
    # courts = Shape("layers/quilantos/31024/canchas.shp")
    # rivers = Shape("layers/quilantos/31024/hidro.shp")
    # tessellator('quilantos_31024', sizes, usos, slope, roads, courts, rivers)
    # print 'quilantos_31024'

    # usos = Shape("layers/quilantos/31025/usos.shp")
    # slope = Shape("layers/quilantos/31025/pendi.shp")
    # roads = Shape("layers/quilantos/31025/caminos.shp")
    # courts = Shape("layers/quilantos/31025/canchas.shp")
    # # rivers = Shape("layers/quilantos/31025/hidro.shp")
    # tessellator('quilantos_31025', sizes, usos, slope, roads, courts)
    # print 'quilantos_31025'

    # usos = Shape("layers/quilantos/31039/usos.shp")
    # slope = Shape("layers/quilantos/31039/pendi.shp")
    # roads = Shape("layers/quilantos/31039/caminos.shp")
    # courts = Shape("layers/quilantos/31039/canchas.shp")
    # # rivers = Shape("layers/quilantos/31039/hidro.shp")
    # tessellator('quilantos_31039', sizes, usos, slope, roads, courts)
    # print 'quilantos_31039'

    # usos = Shape("layers/quilantos/31056/usos.shp")
    # slope = Shape("layers/quilantos/31056/pendi.shp")
    # roads = Shape("layers/quilantos/31056/caminos.shp")
    # courts = Shape("layers/quilantos/31056/canchas.shp")
    # tessellator('quilantos_31056', sizes, usos, slope, roads, courts)
    # print 'quilantos_31056'
