# -*- coding: utf-8 -*-
import math
from random import choice, randint, random

# import fiona
from shapely.geometry import mapping, shape, Point, LineString
from shapely.ops import unary_union, polygonize
from shapely.geos import TopologicalError
#Clases
import settings
import utils
from shape import *

import voronoi.voronoi_poly as voro


#Distancia que se considera cerca un camino o rodal
near_distance_road = 200.0
near_distance_court = 30.0
#Profundidad del Hill climbing
depth_search = 100
#Voro box
box = [1000000000, -1000000000, -1000000000, 1000000000]


def get_npoints(feature, maxsize):
    """
    Función que estima el número de puntos en que debería ser cortado
    la geometría
    """
    geom = shape(feature['geometry'])
    npoints = math.ceil(geom.area / maxsize)
    # Hack, Mi implementacion de Voronoi no funciona con dos puntos
    if npoints <= 2:
        npoints = 3
    return npoints


def voronoi_tessellation(feature, courts_shape, roads_shape, maxsize):

    npoints = get_npoints(feature, maxsize)
    candidates = get_candidates_points(feature, courts_shape, roads_shape)
    voro_features = sa_voronoi(feature, candidates, npoints, maxsize)

    if voro_features is None:
        invalids = []
    elif len(voro_features) < 1:
        invalids = []
    else:
        invalids = get_invalids(voro_features, maxsize)
    # Extra tesselation if still are invalid polygons
    # for invalid in invalids:
    #     print "Procces invalid polygons"
    #     candidates = get_candidates_points(invalid, courts_shape, roads_shape)
    #     npoints = get_npoints(invalid, maxsize)
    #     new_polygons = sa_voronoi(invalid, candidates, npoints, maxsize)
    #     voro_features.remove(invalid)
    #     voro_features.extend(new_polygons)
    # #shape_voro.add_features(voro_features)
    return voro_features


def get_candidates_points(
        feature, courts_shape, roads_shape, with_extra=False):
    """
    Retorna todos los puntos candidatos para realizar el teselado
    de la geometría.
    El orden de consideración es: canchas, caminos, contornos de la geometría
    """
    candidates = []
    courtpoints = court_points(feature, courts_shape)
    roadpoints = road_points(feature, roads_shape)
    if len(courtpoints) > 0:
        candidates = courtpoints
        if with_extra:
            if len(roadpoints) > 0:
                candidates.extend(roadpoints)

            else:
                geopoints = geometric_points(feature)
                candidates.extend(geopoints)

    elif len(roadpoints) > 0:
        candidates = roadpoints
        if with_extra:
            geopoints = geometric_points(feature)
            candidates.extend(geopoints)

    else:
        candidates = geometric_points(feature)
    # print len(candidates), len(set(candidates))
    return _uniq(candidates)


def _uniq(candidates):
    """
    Se asegura que todos los elementos de una lista sean unicos
    preservando el orden.
    """
    uniques = list()
    for c in candidates:
        if c not in uniques:
            uniques.append(c)
    return uniques


def road_points(feature, roads_shape):
    """
    Retorna todos los puntos pertencecientes a los contornos (buffer)
    de los caminos que están dentro de la geometría a teselar
    """
    geom = shape(feature['geometry'])
    roads = roads_shape.get_features()
    candidates = []
    for road in roads:
        groad = shape(road['geometry'])
        gbroad = groad.buffer(near_distance_road)
        intersect = geom.intersection(gbroad)
        if not intersect.is_empty:
            if intersect.geom_type == "Polygon":
                candidates.extend(list(intersect.exterior.coords))
            elif intersect.geom_type == "MultiPolygon":
                for polygon in intersect:
                    candidates.extend(list(polygon.exterior.coords))
    return candidates


def court_points(feature, courts_shape):
    """
    Retorna todos los puntos de contorno de las canchas que están
    dentro de la geometría a teselar.
    """
    geom = shape(feature['geometry'])
    courts = courts_shape.get_features()
    candidates = []
    for court in courts:
        gcourt = shape(court['geometry'])
        gbcourt = gcourt.buffer(near_distance_court, 16)
        intersect = geom.convex_hull.intersection(gbcourt)

        if not intersect.is_empty:
            # print "feature:", feature['properties']['USOS_ID'],
            # " cancha:", court['properties']['ID_CANCHA']
            candidates.extend(list(gbcourt.exterior.coords))
    return candidates


def geometric_points(feature):
    """
    Retorna una lista con todos los puntos pertencecientes
    al contorno de la geometría
    """
    geom = shape(feature['geometry'])
    #shape_voro = Shape("temp/voro.shp", settings.usos_schema, True)
    candidates = list(geom.exterior.coords)
    return candidates


def choice2_points(candidates, npoints):
    """
    Se diferencia de choice_points en que retorna una lista
    y preserva el orden de los puntos
    """
    voro_points = list()

    # Verificamos si se pueden generar los puntos
    n_p = len(set(candidates))
    if n_p < npoints:
        print "No hay suficientes puntos"
        npoints = n_p

    while len(voro_points) < npoints:
        point = choice(candidates)
        index = candidates.index(point)
        if {"index": index, "point": point} not in voro_points:
            voro_points.append({"index": index, "point": point})
    # ordenamos los puntos
    voro_points = sorted(voro_points, key=lambda k: k['index'])
    sorted_voro_points = list()
    for p in voro_points:
        sorted_voro_points.append(p['point'])

    return sorted_voro_points


def clever_operator(candidates, current_solution, features, maxsize):
    """
    Trata de seleccionar puntos que esten dentro
    de poligonos que violen la restriccion de superficie
    maxima
    """
    invalids = get_invalids(features, maxsize)
    conflict_points = list()
    for point in current_solution:
        for polygon in invalids:
            geom_point = Point(point[0], point[1])
            geom_pol = shape(polygon['geometry'])
            if geom_point.within(geom_pol):
                # print "clever operator"
                conflict_points.append(point)

    if len(conflict_points) > 0:
        selected = choice(conflict_points)
    else:
        selected = choice(current_solution)

    return simple_operator(candidates, current_solution, selected)


def simple_operator(candidates, current_solution, selected=None):
    if selected is None:
        selected = choice(current_solution)  # Seleccionamos un punto para modificarlo
    pos_in_sol = current_solution.index(selected)
    if pos_in_sol > 0:
        left_border = candidates.index(current_solution[pos_in_sol - 1]) + 1
    else:
        left_border = 0

    if pos_in_sol < len(current_solution) - 1:
        right_border = candidates.index(current_solution[pos_in_sol + 1]) - 1
    else:
        right_border = len(candidates) - 1
    # En este caso no hay nada que hacer
    # retornamos la misma solucion
    if (left_border == pos_in_sol
            and right_border == pos_in_sol):
        print "misma solucion"
        return current_solution

    if left_border == right_border:
        #print "Mismos bordes"
        return current_solution

    if left_border >= right_border:
        #print "left_border >= right_border"
        # print "reorder:", left_border, right_border, candidates.index(current_solution[pos_in_sol])
        left_border, right_border = right_border, left_border
        # return current_solution

    # Horrible hack
    if right_border - left_border <= 3:
        left_border = 0
        right_border = len(candidates) - 1

    global_pos = candidates.index(selected)
    # Evitamos que el nuevo punto ya este en la solucion
    new_point = selected
    count = 0
    while new_point in current_solution:
        count += 1
        # Hack
        if right_border > len(candidates) - 1:
            print "WTF: Borde derecho mayor", len(candidates) - 1, right_border
            right_border = len(candidates) - 1
        new_point = candidates[randint(left_border, right_border)]
        if count % 100 == 0:
            #print "Loop infinito"
            if left_border > 0:
                left_border -= 1
            else:
                left_border = 0

            if right_border < len(candidates) - 1:
                right_border += 1
            else:
                right_border = len(candidates) - 1

    current_solution[pos_in_sol] = new_point
    return current_solution


def sa_voronoi(feature=None, candidates=None, npoints=None, maxsize=None, operator="mixed", debug=False):
    """
    Simulated annealing Algorithm
    """
    geom = shape(feature['geometry'])
    area = geom.area
    average = area / npoints

    max_iter = 1000  # se aumentan hasta 5 puntos
    iter_ = 0  # Numero de cliclos
    #min_valids_solutions = 20  # ??
    #valids_solutions = 0  # Contador

    T_max = 20000  # Orden del delta fitness
    T = T_max
    T_decr = 200
    searching = True
    restart = False
    history = list()

    # First solution (random points)
    # Hack para cuando no se puede generar Voronoi
    result_features = False
    while result_features is False:
        #print npoints
        solution = choice2_points(candidates, npoints)
        # result_features = voronoi(feature, solution)
        result_features = scipy_voro(feature, solution)

    new_fitness = get_stdev_fitness(result_features, average, maxsize)
    history.append(new_fitness)
    best = {'features': result_features, 'fitness': new_fitness}
    best_off_all = {'features': result_features, 'fitness': new_fitness}
    best_invalid = {'features': result_features, 'fitness': new_fitness}

    while searching and npoints <= len(set(candidates)):
        if iter_ % 100 == 0:
            pass
            # print iter_, feature['properties']['USOS_ID'], valids_solutions
        accepted = False
        if restart:
            T = T_max
            solution = choice2_points(candidates, npoints)
            # En el prox restart se aumenta el n de puntos
            npoints += 1
        else:
            # Escoger nueva solución de la vecindad
            past_solution = solution
            if operator == "simple":
                solution = simple_operator(candidates, solution)
            elif operator == "clever":
                solution = clever_operator(candidates, solution, result_features, maxsize)
            elif operator == "mixed":
                if random() <= 0.9:
                    solution = clever_operator(candidates, solution, result_features, maxsize)
                else:
                    solution = simple_operator(candidates, solution)

         #temp_features = voronoi(feature, solution)
        temp_features = scipy_voro(feature, solution)

        if temp_features is not False:
            result_features = temp_features
            restart = False
            new_fitness = get_stdev_fitness(result_features, average, maxsize)
            delta_e = new_fitness - best['fitness']
            # invalids = get_invalids(result_features, maxsize)
            if delta_e <= 0:
                accepted = True
            else:
                prob = math.exp(float(-delta_e) / float(T))
                if random() <= prob:
                    accepted = True

            # Actualizamos T en un esquema lineal
            T = T - T_decr
            if T <= 0:
                restart = True

            # Guardamos la solucion si correspone
            
            if accepted:
                # if len(invalids) == 0:
                best['features'] = result_features
                best['fitness'] = new_fitness

                if new_fitness < best_off_all['fitness']:
                    best_off_all['features'] = result_features
                    best_off_all['fitness'] = new_fitness

                # else:
                #     if new_fitness <= best_invalid['fitness']:
                #         best_invalid['features'] = result_features
                #         best_invalid['fitness'] = new_fitness

        else:
            print "No se pudo aplicar Voronoi", iter_

        # Actualizamos los contadores
        iter_ += 1
        if iter_ >= max_iter:
            # Detenemos la busqueda
            searching = False

        history.append(best['fitness'])

    # Retornamos la mejor solucion
    if best_off_all['features'] is None:
        # has not found a valid solution- Choice the best invalid solution!!
        print "USO_ID: {0} has not found a valid solution".format(
            feature['properties']['USOS_ID'])
        if debug:
            return best_invalid['features'], history
        else:
            return best_invalid['features']
    else:
        if debug:
            return best_off_all['features'], history
        else:
            return best_off_all['features']


def get_invalids(features, maxsize):
    """Return the number of polygons that
    don't meet the max size restriction"""
    invalids = []
    for f in features:
        geom = shape(f['geometry'])
        if geom.area > maxsize:
            invalids.append(f)
    return invalids


def get_stdev_fitness(features, average_area, maxsize=None):
    """
    Obtiene la desviacion estandar respecto a
    la media esperada.
    """
    sum_ = 0
    n = len(features)
    # for feat in features:
    #     geom = shape(feat['geometry'])
    #     sum_ = (geom.area - average_area) ** 2
    # stdev = math.sqrt(sum_ / n)
    # areas = list()
    convex_metric = 0
    for feat in features:
        geom = shape(feat['geometry'])
        convex_metric += convexity(geom)

    import numpy
    stdev = numpy.std(map(lambda f: shape(f['geometry']).area, features))
    if maxsize is not None:
        invalids = get_invalids(features, maxsize)
    else:
        invalids = 0
    fitness = stdev + (n * stdev / 2) + (len(invalids) * stdev) + convex_metric
    return fitness


def convexity(geom):
    """
    Retorna un valor representado el grado de convexidad del poligono
    A mayor valor menor convexidad.
    """
    convex = geom.convex_hull
    diff = convex.difference(geom)
    return diff.area * 0.1


def scipy_voro(feature, points):
    geom = shape(feature['geometry'])
    from scipy.spatial import Voronoi as sci_voronoi
    magic_points = [(10000000, 10000000), (10000000, -10000000), (-10000000, 10000000), (-10000000, -10000000)]
    the_voro_points = points + magic_points
    vor = sci_voronoi(the_voro_points)
    lines = [
        LineString(vor.vertices[line])
        for line in vor.ridge_vertices
        if -1 not in line]

    voro_polygons = list()
    for poly in polygonize(lines):
        voro_polygons.append(poly)

    final = list()
    for vp in voro_polygons:
        final.append(geom.intersection(vp))

    # final_union = unary_union(final)
    if len(final) < 1:
        return False

    voro_features = []
    index = 0
    for polygon in final:
        if polygon.geom_type == "Polygon":
            f = {}
            f['properties'] = {}
            f['geometry'] = mapping(polygon)
            f['properties'] = feature['properties'].copy()
            f['properties'][u'AREA'] = polygon.area
            f['properties'][u'PERIMETER'] = polygon.length
            f['properties'][u'USOS_ID'] = utils.make_uso_id(
                feature['properties']['USOS_ID'], index)
            voro_features.append(f)
            index = index + 1
        elif polygon.geom_type in ["MultiPolygon", "GeometryCollection"]:
            for part in polygon:
                f = {}
                f['properties'] = {}
                f['geometry'] = mapping(part)
                f['properties'] = feature['properties'].copy()
                f['properties'][u'AREA'] = part.area
                f['properties'][u'PERIMETER'] = polygon.length
                f['properties'][u'USOS_ID'] = utils.make_uso_id(
                    feature['properties']['USOS_ID'], index)
                voro_features.append(f)
                index = index + 1

    return voro_features


def test_operators(usos, roads, courts, max_size, operator, file_name):
    max_size *= 10000
    features = []
    context = settings.Context(usos.schema.copy())
    final = Shape(
        "test_outputs_operators" + os.sep + file_name + ".shp",
        context.usos_schema, True)
    for f in usos.get_features():
        geom = shape(f['geometry'])
        if geom.area > max_size:
            npoints = get_npoints(f, max_size)
            candidates = get_candidates_points(f, courts, roads)
            new_features, history = sa_voronoi(
                f, candidates, npoints, max_size, operator, debug=True)

            if new_features is None:
                print "Error None Type: ", f['properties']['USOS_ID']
            else:
                features.extend(new_features)
                # Guardar las estadisticas
                import csv
                with open("test_outputs_operators" + os.sep + file_name + ".csv", 'wb') as myfile:
                    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                    for fitness in history:
                        wr.writerow([fitness])

                    wr.writerow([])
                    minimum = min(history)
                    wr.writerow(["Minimo", minimum])
                    index = history.index(minimum)
                    wr.writerow(["index", index])

        else:
            features.append(f)

    final.add_features(features)


def test_statistics(shape_file):
    areas = list()
    n = 0
    for f in shape_file.get_features():
        geom = shape(f["geometry"])
        areas.append(geom.area)
        n += 1
    maximum = max(areas)
    minimum = min(areas)
    import numpy
    stdev = numpy.std(areas)


if __name__ == "__main__":

    def operators():

        # tests = {"elena_la1": 2.9, "collico_2": 0.74, "sta_carla": 1.25}
        tests = {"elena_la1": 2.9}
        #tests = {"collico_2": 0.74}
        #tests = {"sta_carla": 1.25}

        for key, value in tests.iteritems():
            usos = Shape("test_polygons/{}/usos.shp".format(key))
            # Teselado orientado a canchas
            roads = Shape("test_polygons/{}/no_caminos.shp".format(key))
            courts = Shape("test_polygons/{}/canchas.shp".format(key))
            test_operators(
                usos, roads, courts, value, "simple",
                "{}/result_canchas_simple".format(key))
            test_operators(
                usos, roads, courts, value, "clever",
                "{}/result_canchas_clever".format(key))
            test_operators(
                usos, roads, courts, value, "mixed",
                "{}/result_canchas_mixed".format(key))
            # # Teselado orientado a caminos
            # roads = Shape("test_polygons/{}/caminos.shp".format(key))
            # courts = Shape("test_polygons/{}/no_canchas.shp".format(key))
            # test_operators(
            #     usos, roads, courts, value,
            #     True, "{}/result_caminos_simple".format(key))
            # test_operators(
            #     usos, roads, courts, value,
            #     False, "{}/result_caminos_clever".format(key))
            # # Sta carla Geometrico
            # roads = Shape("test_polygons/{}/no_caminos.shp".format(key))
            # courts = Shape("test_polygons/{}/no_canchas.shp".format(key))
            # test_operators(
            #     usos, roads, courts, value, True,
            #     "{}/result_geometrico_simple".format(key))
            # test_operators(
            #     usos, roads, courts, value, False,
            #     "{}/result_geometrico_clever".format(key))

    operators()
