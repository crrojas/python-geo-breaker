# -*- coding: utf-8 -*-
"""
1.-Crear polígonos que definan el alcance de cada cancha
2.-Obtener la intersección entre cada cancha y pendiente que puede cosechar
"""
#Geospatial libraries
import fiona
from shapely.geometry import mapping, shape, MultiPolygon
from shapely.ops import cascaded_union
#Clases
import settings
import utils
from shape import *
import geo


def simplify_slope(slope_shape):
    """Unificación de pendientes según tipo de equipo"""
    slopes = slope_shape.get_features()
    grappler = []
    skhu = []
    tower = []
    properties = slopes[0]['properties']
    for fs in slopes:
        slope_geom = shape(fs['geometry'])
        slope_code = int(fs['properties']['SLOPE_CODE']) - settings.slope_interval #Parametrizar esto!!
        # if slope_code <= settings.max_equi_slope['GRAPPLER']
        #     grappler.append(slope_geom)
        if slope_code <= settings.max_equi_slope['SKHU']:
            skhu.append(slope_geom)
        elif slope_code >= settings.min_equi_slope['TORR'] and slope_code <= settings.max_equi_slope['TORR']:
            tower.append(slope_geom)
        else:
            print "XD"

    #grappler_surface = cascaded_union(grappler)
    #print 'grappler_surface', grappler_surface.geom_type, len(grappler_surface)
    skhu_surface = cascaded_union(skhu)
    print 'skhu_surface', skhu_surface.geom_type, len(skhu_surface)
    tower_surface = cascaded_union(tower)
    print 'tower_surface', tower_surface.geom_type, len(tower_surface)

    #Eliminamos los polygonos de la superficie de skhuque son muy pequeños
    significant_skhu_polys = []
    for polygon in skhu_surface:
        if polygon.area >= settings.min_surface:
            significant_skhu_polys.append(polygon)
        else:
            tower_surface = tower_surface.union(polygon)

    skhu_surface = cascaded_union(significant_skhu_polys)

    #Eliminamos los polygonos que son muy pequeños
    significant_tower_polys = []
    for polygon in tower_surface:
        if polygon.area >= settings.min_surface:
            significant_tower_polys.append(polygon)
        else:
            skhu_surface = skhu_surface.union(polygon)

    tower_surface = cascaded_union(significant_tower_polys)

    #utils.to_feature(tower_surface)
    #print len(skhu_surface)
    final = Shape("temp/simplify_slope.shp", settings.slope_equi_schema, True)
    #final.add_features([utils.to_feature(grappler_surface, {'TIPO':'GRAPPLER', 'PENDIMAX':20})])

    fskhu = utils.to_feature(skhu_surface, {'TIPO': 'SKHU', 'SLOPE_CODE': 30})
    ftower = utils.to_feature(tower_surface, {'TIPO': 'TORR', 'SLOPE_CODE': 100})
    final.add_features([fskhu])
    final.add_features([ftower])
    #simplify_slope ={'SKHU': fskhu, 'TORR': ftower}
    simplify_slope = [fskhu, ftower]
    return simplify_slope


#Retorna un feature con el alcance de la pendiente
def court_scope(court, slope):

    courts_scope = []
    #Polígonos que representan las pendientes
    #fslopes = slope.get_features()
    fslopes = slope
    fc = court
    ktype = fc['properties']['TIPO']
    #obtenemos el alcance de la cancha según su tipo
    distance = settings.courts_scope[ktype]
    #obtenemos la mínima pendiente permitida para el tipo de equipo
    min_slope = settings.min_equi_slope[ktype]
    #obtenemos la máxima pendiente permitida para el tipo de equipo
    max_slope = settings.max_equi_slope[ktype]
    #print distance, min_slope, max_slope
    court_geom = shape(fc['geometry'])
    pscope = court_geom.buffer(distance)

    print "Calculando superficie de alcance para la cancha: ", fc['properties']['ID_CANCHA'], fc['properties']['TIPO']
    for fs in fslopes:
        slope = int(fs['properties']['SLOPE_CODE']) - 5 #Parametrizar esto!!
        #print slope
        #Si le pendiente se encuentra en el rango de operación de la cancha
        if slope >= min_slope and slope <= max_slope:
            slope_geom = shape(fs['geometry'])
            #print "pendiente: ",fs['properties']['SLOPE_CODE']
            scope_int_slope = pscope.intersection(slope_geom)
            if scope_int_slope.geom_type == 'Polygon':
                surface = scope_int_slope
                pass
            elif scope_int_slope.geom_type in ['MultiPolygon', 'GeometryCollection'] :
                surface = cascaded_union(scope_int_slope.geoms)
            else:
                print scope_int_slope.geom_type

            courts_scope.append(surface)
            # fscope = {}
            # fscope['geometry'] = mapping(surface)
            # fscope['properties'] = fc['properties']
            # courts_scope.append(fscope)
    total_surface = cascaded_union(courts_scope)

    # if total_surface.geom_type == 'MultiPolygon':

    #     polygons = []
    #     for pp in total_surface.geoms:
    #         if pp.area >= settings.min_surface:
    #             polygons.append(pp)
    #     final_surface = MultiPolygon(polygons)
    # else:
    #     final_surface = total_surface

    fscope = {}
    fscope['geometry'] = mapping(total_surface)
    fscope['properties'] = fc['properties']
    return fscope


def slope_slice(contour, slopes):

    usos = []
    for c in contour:
        cgeom = shape(c['geometry'])
        for s in slopes:
            sgeom = shape(s['geometry'])
            c_s = cgeom.intersection(sgeom)
            if c_s.geom_type == 'MultiPolygon':
                usos.extend(utils.to_features(c_s, properties={'TIPO': 'USO', 'EQUIPO': s['properties']['TIPO']}))
            elif c_s.geom_type == 'Polygon':
                usos.extend([utils.to_feature(c_s, properties={'TIPO': 'USO', 'EQUIPO': s['properties']['TIPO']})])
    return usos

def court_neighbor_tessellation(court_scope, neighbor):
    pass


if __name__ == "__main__":

    usos = Shape("layers/elena_la1/usos.shp")
    courts = Shape("layers/elena_la1/canchas.shp")
    slope = Shape("layers/elena_la1/pendi.shp")
    roads = Shape("layers/elena_la1/caminos.shp")
    rivers = Shape("layers/elena_la1/hidro.shp")

    # for f in courts.get_features():
    #     print f['properties']['TIPO']
    # slope = Shape("layers/elena_la1/pendi.shp", settings.pendi_schema)
    # for x in slope.get_features():
    #     print x['properties']['RANGO']

    ss = simplify_slope(slope)

    features = []
    # for cf in courts.get_features():
    #     cscope = court_scope(cf, ss)
    #     features.append(cscope)

    # cfs = courts.get_features()
    # cf = cfs[1]
    # cscope = court_scope(cf, ss)
    contour = geo.contour(usos)
    usos_generados = slope_slice(contour, ss)


    #features.extend(utils.to_features(shape(cscope['geometry']), cscope['properties']))
    #features.append(cscope)

    final = Shape("temp/usos_generados.shp", settings.usos_generados_schema, True)
    final.add_features(usos_generados)