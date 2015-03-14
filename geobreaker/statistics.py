# -*- coding: utf-8 -*-
import os
import math
import csv
from shape import Shape
from shapely.geometry import shape

import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

hectarea = 10000


def collect_statistics(folder, file_name='statistics.csv'):
    files = os.listdir(folder)
    files.sort()
    table = list()
    sizes = list()
    to_boxplot = list()
    for f in files:
        name, ext = os.path.splitext(f)
        if ext == '.shp':
            temp_shape = Shape('{0}{1}{2}'.format(folder, os.sep, f))
            parts = name.split('_')
            stage = parts[0]
            maxsize = parts[1]
            statistics = temp_shape.statistics(maxsize)
            table.append({'stage': stage,
                         'maxsize': maxsize,
                         'statistics': statistics})

            # Make Histogram chart
            histogram(
                statistics['sizes'],
                10,
                statistics['mean'],
                statistics['std'],
                name,
                '{0}{1}{2}{3}.{4}'.format(
                    folder, os.sep, os.sep, name, 'png'))

            to_boxplot.append(statistics['sizes'])

            accum = 0
            q = 0

            sizes.extend(['', '', ''])
            sizes.append(name)
            for feat in temp_shape.get_features():
                area = shape(feat['geometry']).area
                sizes.append(area)
                accum += area
                q += 1
            avg = accum / q
            x_i = 0
            for feat2 in temp_shape.get_features():
                area2 = shape(feat2['geometry']).area
                x_i += (area2 - avg) ** 2
            std = math.sqrt(x_i / q)
            sizes.append(['Stdev', std])

    with open(file_name, 'wb') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=';')

        for s in sizes:
            if type(s) == list:
                csvwriter.writerow([str(x).replace('.', ',') for x in s])
            else:
                csvwriter.writerow([str(s).replace('.', ',')])

        csvwriter.writerow([])
        csvwriter.writerow([])

        csvwriter.writerow(['', 5, 10, 15, 20])

        csvwriter.writerow(['geo'])
        write_data(csvwriter, 'geo', table)

        csvwriter.writerow(['voro'])
        write_data(csvwriter, 'voro', table)

        csvwriter.writerow(['merge'])
        write_data(csvwriter, 'merge', table)

    geo_5 = find_(table, 'geo', '5', 'sizes', False)
    voro_5 = find_(table, 'voro', '5', 'sizes', False)
    merge_5 = find_(table, 'merge', '5', 'sizes', False)
    box_plot(
        [geo_5, voro_5, merge_5],
        5, '{0}{1}box_plot_5.png'.format(folder, os.sep))

    geo_10 = find_(table, 'geo', '10', 'sizes', False)
    voro_10 = find_(table, 'voro', '10', 'sizes', False)
    merge_10 = find_(table, 'merge', '10', 'sizes', False)
    box_plot(
        [geo_10, voro_10, merge_10],
        10, '{0}{1}box_plot_10.png'.format(folder, os.sep))

    geo_15 = find_(table, 'geo', '15', 'sizes', False)
    voro_15 = find_(table, 'voro', '15', 'sizes', False)
    merge_15 = find_(table, 'merge', '15', 'sizes', False)
    box_plot(
        [geo_15, voro_15, merge_15],
        15, '{0}{1}box_plot_15.png'.format(folder, os.sep))

    geo_20 = find_(table, 'geo', '20', 'sizes', False)
    voro_20 = find_(table, 'voro', '20', 'sizes', False)
    merge_20 = find_(table, 'merge', '20', 'sizes', False)
    box_plot(
        [geo_20, voro_20, merge_20],
        20, '{0}{1}box_plot_20.png'.format(folder, os.sep))

    return table


def write_data(csvwriter, title, table):

    def write_group(csvwriter, param, table, columns=['5', '10', '15', '20']):
        row = [param]
        row.extend([find_(table, title, x, param) for x in columns])
        csvwriter.writerow(row)

    write_group(csvwriter, 'qty', table)
    write_group(csvwriter, 'mean', table)
    write_group(csvwriter, 'std', table)
    write_group(csvwriter, 'maximun', table)
    write_group(csvwriter, 'minimun', table)
    write_group(csvwriter, 'fails', table)
    write_group(csvwriter, 'q25', table)
    write_group(csvwriter, 'q50', table)
    write_group(csvwriter, 'q75', table)


def find_(table, stage, maxsize, value, replace=True):
    for t in table:
        if t['stage'] == stage and t['maxsize'] == maxsize:
            if replace:
                return str(t['statistics'][value]).replace('.', ',')
            else:
                return t['statistics'][value]
    return False


def histogram(serie, bins, mu, sigma, title, file_name='chart.png', color='green'):

    num_bins = bins
    # the histogram of the data
    n, bins, patches = plt.hist(
        serie, num_bins, normed=False, facecolor=color, alpha=0.5)
    # add a 'best fit' line
    y = mlab.normpdf(bins, mu, sigma)
    plt.plot(bins, y, 'r--')
    plt.xlabel('Superficie (ha)')
    plt.ylabel(u'Cantidad de polígonos')
    plt.title(
        r'Histograma {0}'.
        format(title))

    # Tweak spacing to prevent clipping of ylabel
    plt.subplots_adjust(left=0.15)
    plt.savefig(file_name, bbox_inches='tight')
    plt.close()


def box_plot(data, maxsize, file_name='chart.png'):

    bp = plt.boxplot(data, notch=False, sym='.', vert=1, whis=1.5)
    plt.axhline(y=maxsize)
    plt.title("Cuartiles")
    plt.xlabel('Etapa')
    plt.ylabel('ha')
    plt.xticks([1, 2, 3], [u'geografía', u'accesos', u'integración'])
    plt.subplots_adjust(left=0.15)
    plt.savefig(file_name, bbox_inches='tight')
    plt.close()


def origin_shape(file_name, maxsize, title="Histograma", chart_name='chart.png'):
    temp_shape = Shape(file_name)
    statistics = temp_shape.statistics(maxsize)
    # Make Histogram chart
    histogram(
        statistics['sizes'],
        10,
        statistics['mean'],
        statistics['std'],
        title,
        chart_name,
        'yellow')


if __name__ == "__main__":
    collect_statistics(
        'temp/elena_la1',
        'temp/elena_la1_statistics.csv')
    print 'elena_la1'

    # collect_statistics(
    #     'temp/collico_2',
    #     'temp/collico_2_statistics.csv')
    # print 'collico_2'

    # collect_statistics(
    #     'temp/san_ramon',
    #     'temp/san_ramon_statistics.csv')
    # print 'san_ramon'

    # collect_statistics(
    #     'temp/san_ramon_sur',
    #     'temp/san_ramon_sur_statistics.csv')
    # print 'san_ramon_sur'

    # collect_statistics(
    #     'temp/sta_carla',
    #     'temp/sta_carla_statistics.csv')
    # print 'sta_carla'

    # collect_statistics(
    #     'temp/quilantos_31022',
    #     'temp/quilantos_31022_statistics.csv')
    # print 'quilantos_31022'

    # collect_statistics(
    #     'temp/quilantos_31023',
    #     'temp/quilantos_31023_statistics.csv')
    # print 'quilantos_31023'

    # collect_statistics(
    #     'temp/quilantos_31024',
    #     'temp/quilantos_31024_statistics.csv')
    # print 'quilantos_31024'

    # collect_statistics(
    #     'temp/quilantos_31025',
    #     'temp/quilantos_31025_statistics.csv')
    # print 'quilantos_31025'

    # collect_statistics(
    #     'temp/quilantos_31039',
    #     'temp/quilantos_31039_statistics.csv')
    # print 'quilantos_31039'

    # collect_statistics(
    #     'temp/quilantos_31056',
    #     'temp/quilantos_31056_statistics.csv')
    # print 'quilantos_31056'

    # collect_statistics(
    #     'temp/elena_la1',
    #     'temp/elena_la1_statistics.csv')
    # print 'elena_la1'
