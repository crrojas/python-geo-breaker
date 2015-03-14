def choice_points(candidates, npoints, tabu_list=None):
    """Return a set of points that are not in tabu_list"""
    voro_points = {}
    key = 0
    while len(voro_points) < npoints:
        point = choice(candidates)
        if point not in voro_points:
            voro_points[str(key)] = point
            key = key + 1
        if len(voro_points) == npoints:
            # Check if new voro_points are in tabu list
            if tabu_list is not None:
                if voro_points not in tabu_list:
                    tabu_list.append(voro_points)
                else:
                    print "Voro points in tabu list"
                    # Clear selected points and search other comb.
                    voro_points.clear()
    return voro_points


def get_fitness(features, average_area, invalids=None):
    """Bigger is worst"""
    # factor = 1 + len(invalids)  # punish invalids solutions
    fitness = 0
    for feat in features:
        geom = shape(feat['geometry'])
        area = geom.area
        fitness = fitness + abs(area - average_area)
    return fitness


def voronoi(feature, points):
    geom = shape(feature['geometry'])
    try:
        # Horrible Hack para trabajar con listas """"
        if type(points) == list:
            dict_points = dict()
            for i in range(len(points)):
                dict_points[str(i)] = points[i]
            points = dict_points
        # Fin del horrible hack !!!!!!!!!!!!!!!!!!!!
        voro_polygons = voro.VoronoiPolygons(
            points, BoundingBox=box, PlotMap=False)
        final = []
        for key, value in voro_polygons.items():
            voro_poly = value['obj_polygon']
            try:
                final.append(geom.intersection(voro_poly))
            except TopologicalError:
                # print "TopologicalError: The operation 'GEOSIntersection_r' produced a null geometry"
                return False

        try:
            final_union = unary_union(final)
        except ValueError:
            # print "Error: No Shapely geometry can be created from null value"
            return False

        try:
            diff = geom.difference(final_union)
        #Se adjunta sólo si es relevante
            if (not diff.is_empty) and\
                (diff.area >= (geom.area / len(points)) / 100.0 * 5.0):
                final.append(diff)
        except TopologicalError:
            # print "voro.vornoi: Error desconocido"
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
            else:
                # print "voronoi: caso no tratado", polygon.geom_type
                return False

        return voro_features
    except IndexError:
        # print "index error"
        # print "voro.voronoi: Index error f[id]:",\
        #    feature['properties']['USOS_ID']
        return False
    except:
        return False


def hc_voronoi(feature, candidates, npoints, maxsize, debug=False):
    """
    Algoritmo
        ??? ???
    """
    # wildcards = len(candidates) - npoints  # High cost!!
    wildcards = 10
    geom = shape(feature['geometry'])
    area = geom.area
    average = area / npoints
    tabu = []  # List with all combination of points selected
    #print average
    #voro = Shape("temp/voro" + str(int(feature['properties']['USOS_ID']))+
    #".shp", settings.usos_schema, True)
    # best = {'features': None, 'fitness': 9999999999999999}
    # best_invalid = {'features': None, 'fitness': 9999999999999999}
    history = list()

    # First solution (random points)
    # Hack para cuando no se puede generar Voronoi
    result_features = False
    while result_features is False:
        #print npoints
        solution = choice2_points(candidates, npoints)
        result_features = voronoi(feature, solution)

    new_fitness = get_stdev_fitness(result_features, average)
    history.append(new_fitness)
    best = {'features': result_features, 'fitness': new_fitness}
    best_invalid = {'features': result_features, 'fitness': new_fitness}

    while wildcards > 0 and npoints <= len(set(candidates)):
        step = 0
        while step < depth_search:
            step += 1
            voro_points = choice_points(candidates, npoints, tabu)
            result_features = voronoi(feature, voro_points)
            # Checks if all features complaint max size restriction
            if result_features is not False:
                invalids = get_invalids(result_features, maxsize)
                new_fitness = get_stdev_fitness(result_features, average)
                if  len(invalids) == 0:
                    if new_fitness <= best['fitness']:
                        best['features'] = result_features
                        best['fitness'] = new_fitness
                else:
                    if new_fitness <= best_invalid['fitness']:
                        best_invalid['features'] = result_features
                        best_invalid['fitness'] = new_fitness
            
            # At the end of local search (npoints)
            if step == (depth_search - 1):
                npoints += 1
                wildcards -= 1
                print "Increasing number of points: {0} {1} {2}".format(
                    feature['properties']['USOS_ID'], npoints, wildcards)

            history.append(best['fitness'])

    #voro.add_features(best['features'])
    #print "Resultado hc", feature['properties']['AREA'], best['features']
    if best['features'] is None:
        # has not found a valid solution- Choice the best invalid solution!!
        print "USO_ID: {0} has not found a valid solution".format(
                feature['properties']['USOS_ID'])
        if debug:
            return best_invalid['features'], history
        else:
            return best_invalid['features']
    else:
        if debug:
            return best['features'], history
        else:
            return best['features']


def test_heuristics(usos, roads, courts, max_size, sa, file_name):
    max_size *= 10000
    features = []
    context = settings.Context(usos.schema.copy())
    final = Shape(
        "test_outputs" + os.sep + file_name + ".shp",
        context.usos_schema, True)
    for f in usos.get_features():
        geom = shape(f['geometry'])
        if geom.area > max_size:
            npoints = get_npoints(f, max_size)
            candidates = get_candidates_points(f, courts, roads)
            if sa:
                new_features, history = sa_voronoi(
                    f, candidates, npoints, max_size, debug=True)
            else:
                new_features, history = hc_voronoi(
                    f, candidates, npoints, max_size, debug=True)

            if new_features is None:
                print "Error None Type: ", f['properties']['USOS_ID']
            else:
                features.extend(new_features)
                # Guardar las estadisticas
                import csv
                with open("test_outputs" + os.sep + file_name + ".csv", 'wb') as myfile:
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


    def heuristics():

        tests = {"elena_la1": 2.9, "collico_2": 0.74, "sta_carla": 1.25}

        for key, value in tests.iteritems():
            usos = Shape("test_polygons/{}/usos.shp".format(key))
            # Teselado orientado a canchas
            roads = Shape("test_polygons/{}/no_caminos.shp".format(key))
            courts = Shape("test_polygons/{}/canchas.shp".format(key))
            test_heuristics(
                usos, roads, courts, value, True,
                "{}/result_canchas_sa".format(key))
            test_heuristics(
                usos, roads, courts, value, False,
                "{}/result_canchas_hc".format(key))
            # Teselado orientado a caminos
            roads = Shape("test_polygons/{}/caminos.shp".format(key))
            courts = Shape("test_polygons/{}/no_canchas.shp".format(key))
            test_heuristics(
                usos, roads, courts, value,
                True, "{}/result_caminos_sa".format(key))
            test_heuristics(
                usos, roads, courts, value,
                False, "{}/result_caminos_hc".format(key))
            # Sta carla Geometrico
            roads = Shape("test_polygons/{}/no_caminos.shp".format(key))
            courts = Shape("test_polygons/{}/no_canchas.shp".format(key))
            test_heuristics(
                usos, roads, courts, value, True,
                "{}/result_geometrico_sa".format(key))
            test_heuristics(
                usos, roads, courts, value, False,
                "{}/result_geometrico_hc".format(key))