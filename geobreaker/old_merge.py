def merge_(small, features, maxsize):

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

    def get_neighbors(small, features):
        neighbors = []
        geom1 = shape(small['geometry'])
        for f in features:
            geom2 = shape(f['geometry'])
            if geom1 is not geom2:
                if geom1.touches(geom2) and (geom1.area + geom2.area) <= maxsize:
                    neighbors.append(f)
        return neighbors

    def union(features):
        geoms = []
        for f in features:
            g = shape(f['geometry'])
            geoms.append(g)
        return unary_union(geoms)

    def local_search(small, neighbors, maxsize):

        def get_total_area(features):
            total_area = 0
            for f in features:
                geom = shape(f['geometry'])
                total_area += geom.area
            return total_area

        depth_search = 100
        iter_parts = 10
        step = 0
        used = 0
        parts = 2
        first_fitness = abs(maxsize - get_total_area([small]))
        best = {'features': [small], 'fitness': first_fitness}

        if len(neighbors) == 0:
            return best['features']

        while (step < depth_search) and (parts <= len(neighbors) + 1):
            # Possible combinations for the solution size (parts)
            combinations = math.factorial((len(neighbors) + 1))\
                    / math.factorial(parts) * math.factorial((len(neighbors) + 1) - parts) 
            step += 1
            solution = list([small])
            while len(solution) < parts:
                n = choice(neighbors)
                if n not in solution:
                    solution.append(n)
            used += 1
            
            total_area = get_total_area(solution)
            fitness = abs(maxsize - total_area)
            if total_area <= maxsize and fitness <= best['fitness']:
                # print "better solution found"
                best['fitness'] = fitness
                best['features'] = solution

            if (used >= iter_parts) or used >= combinations:
                parts += 1
                used = 0
        return best['features']

    neighbors = get_neighbors(small, features)
    # print "vecinos", len(neighbors)

    solution = local_search(small, neighbors, maxsize)

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
        print "wtf"

    # Removes features used in the solution
    to_remove = list()
    for f in solution[1:]:
        to_remove.append(f)

    return merge_features, to_remove