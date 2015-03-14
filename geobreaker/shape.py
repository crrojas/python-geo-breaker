# -*- coding: utf-8 -*-
#General libraries
import os
import csv
#Geospatial libraries
import fiona
from shapely.geometry import mapping, shape
#Clases
from settings import Context
import numpy


class Shape:
    """ Clase que permite crear shapes de manera simple """
    settings = Context()
    file_name = None
    #Path a las carpetas
    path_layers = "layers" + os.sep
    path_temp = "temp" + os.sep
    #Distancia con la cual se considera que los polígonos son vecinos
    min_neighbors_dist = 90.0  # mts
    #Identificador del archivo shape creado o cargado
    shape = None
    #Arreglo con los features del shape
    features = None

    schema = None

    hectarea = 10000

    #Sistema de referencia de coordenadas por defecto.
    #Los archivos que nos pasaron no tienen uno asignado.
    default_crs = ""

    #Tipo de archivos con los que se trabaja
    default_driver = "ESRI Shapefile"

    def __init__(self, file_name, schema=None, del_if_exits=False):
        self.file_name = file_name
        self.features = []
        self.schema = schema
        if os.path.exists(file_name) and (not del_if_exits):
            #print "Cargando archivo existente"
            self.shape = self.load_shp(file_name)
        else:
            #print "Creando nuevo archivo"
            with fiona.open(file_name, 'w',
                            crs=self.default_crs,
                            driver=self.default_driver,
                            schema=schema) as new_file:

                self.shape = new_file

    def get_min_neighbors_dist(self):
        return self.min_neighbors_dist

    def get_shape(self):
        if self.shape is not None:
            return self.shape
        else:
            print "El shape no es válido"

    def get_path_layers(self):
        return self.path_layers

    def get_features(self):
        return self.features

    # def add_feature(self, feature):
    #     with fiona.open(self.file_name, 'a', self.schema) as shape:
    #         #self.get_shape().write(f)
    #         #self.features.append(feature)
    #         pass

    def add_features(self, features):
        with fiona.open(self.file_name, 'a', self.schema) as shape_file:
            try:
                shape_file.writerecords(features)
                #shape.flush()
                self.features.extend(features)
            except:
                print "Error de tipo"

    def load_shp(self, file_name):
        """Retorna un identificador al archivo shape abierto.
        Además guarda todos los features en el arreglo features[] del objeto"""
        with fiona.open(file_name, 'r') as source:
            # **source.meta is a shortcut to get the crs, driver, and schema
            # keyword arguments from the source Collection.
            #self.shape = source
            self.schema = source.schema.copy()
            for f in source:
                try:
                    geom = shape(f['geometry'])
                    if not geom.is_valid:
                        clean = geom.buffer(0.0)
                        assert clean.is_valid
                        assert clean.geom_type == 'Polygon'
                        geom = clean
                    f['geometry'] = mapping(geom)
                    self.features.append(f)

                except Exception:
                    # Writing uncleanable features to a different shapefile
                    # is another option.
                    #logging.exception("Error cleaning feature %s:", f['id'])
                    #print "Error cleaning feature %s:", f['id']
                    self.features.append(f)
        return source

    def get_geometry(self, feature):
        """Retorna la geometría asociada a un feature."""
        geom = shape(feature['geometry'])
        return geom

    def neighbors_matrix(self, file_name="temp/neighbors_matrix.txt"):
        """Construye una matriz de adyacencia para cada polígono.
        Se considera que dos polígonos son adyacentes si la distancia
        mínima entre ellos es menor a min_neighbors_dist."""
        with open(file_name, 'wb') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=' ')
            for feat1 in self.get_features():
                geom1 = self.get_geometry(feat1)
                for feat2 in self.get_features():
                    geom2 = self.get_geometry(feat2)
                    if geom1.distance(geom2) <= self.get_min_neighbors_dist():
                        id_feat1 = (feat1['properties']['USOS_ID'])
                        id_feat2 = (feat2['properties']['USOS_ID'])
                        if id_feat1 != id_feat2:
                            csvwriter.writerow([id_feat1, id_feat2])

    def save_layer(self, features):

        for feat in features:
            pass

    def greater_than(self, size):
        """Indicates the polygons greaters than
        a given surface and return an array with them
        *size*: The value in hectareas"""
        greaters = []
        for f in self.get_features():
            geom = self.get_geometry(f)
            if (f['properties']['TIPOUSO'] in self.settings.haverstable)\
                    and geom.area > size:
                print f['properties']['TIPOUSO']
                print int(f['properties']['USOS_ID'])
                print float(f['properties']['AREA']) / self.hectarea
                greaters.append(f)
        return greaters

    def statistics_(self, size, file_name="temp/statistics.csv"):
        greaters = self.greater_than(size)

        with open(file_name, 'wb') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=';')
            for feat in self.get_features():
                size_feat = feat['properties'][u'AREA']
                csvwriter.writerow([size_feat])

            csvwriter.writerow([])
            csvwriter.writerow([])
            csvwriter.writerow([])
            csvwriter.writerow([])
            csvwriter.writerow([])
            csvwriter.writerow([])

            for feat in greaters:
                csvwriter.writerow([feat['properties'][u'AREA']])

    def statistics(
            self,
            maxsize,
            file_name=None):

        sizes = list()
        for feat in self.get_features():
            area = shape(feat['geometry']).area
            sizes.append(area / self.hectarea)

        qty = len(sizes)
        mean = numpy.mean(sizes)
        std = numpy.std(sizes)
        maximun = max(sizes)
        minimun = min(sizes)
        fails = len(filter(lambda s: s >= float(maxsize), sizes))
        sort_sizes = sorted(sizes)
        q25 = numpy.percentile(sort_sizes, 25)
        q50 = numpy.percentile(sort_sizes, 50)
        q75 = numpy.percentile(sort_sizes, 75)

        if file_name is not None:
            with open(file_name, 'wb') as csvfile:
                csvwriter = csv.writer(csvfile, delimiter=';')
                for s in sizes:
                    csvwriter.writerow([s])

                csvwriter.writerow([])
                csvwriter.writerow([qty])
                csvwriter.writerow([mean])
                csvwriter.writerow([std])
                csvwriter.writerow([maximun])
                csvwriter.writerow([minimun])
                csvwriter.writerow([fails])
                csvwriter.writerow([q25])
                csvwriter.writerow([q50])
                csvwriter.writerow([q75])
        else:
            return {'sizes': sizes,
                    'qty': qty,
                    'mean': mean,
                    'std': std,
                    'maximun': maximun,
                    'minimun': minimun,
                    'fails': fails,
                    'q25': q25,
                    'q50': q50,
                    'q75': q75}

    def all_areas(self, file_name):

        with open(file_name, 'wb') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=';', quotechar='"')
            for feat in self.get_features():
                size_feat = float(feat['properties'][u'AREA'])
                csvwriter.writerow([size_feat])


if __name__ == "__main__":

    escenario = Shape("layers/collico_2/escenario.shp")
    #escenario.neighbors_matrix('outputs/neighbors_matrix_sta_carla.csv')
    x = escenario.greater_than((20 * 10000))
    print len(x)
