# -*- coding: utf-8 -*-


class Context():
    """Este archivo posee la descripción de la estructura de los shapes de
    entrada al algoritmo. Lamentablemente esto hace que el algoritmo no
    sea genérico"""

    #Supocisiones
    min_surface = 1000  # 1 ha como
    slope_interval = 5

    #Tipos de canchas
    courts_type = ["SKHU", "TORR", "MIXT"]

    #Alcance de canchas en mts
    courts_scope = {"SKHU": 300, "TORR": 450, "GRAPPLER": 500, "MIXT": 450}

    #Pendiente mínima factible para equipos en porcentaje
    min_feasible_equi_slope = {"SKHU": 0, "TORR": 12, "GRAPPLER": 0, "MIXT": 0}

    #Pendiente mínima de equipos en porcentajes
    min_equi_slope = {"SKHU": 0, "TORR": 30, "GRAPPLER": 0, "MIXT": 0}

    #Pendiente máxima de equipos en porcentaje
    max_equi_slope = {"SKHU": 30, "TORR": 100, "GRAPPLER": 20, "MIXT": 100}

    #Tipos de uso que son cosechales
    haverstable = ['PIRA', 'EUGL', 'EUNI', 'EUDE', 'PIOR']  # Qué es RFRM

    #Schemas genéricos
    #geometrycollection_schema = {'geometry': 'GeometryCollection',
                            # 'properties':{}}
    multipolygon_schema = {'geometry': 'MultiPolygon',
                            'properties': {u'ID': 'int'}}
    polygon_schema = {'geometry': 'Polygon',
                            'properties': {u'ID': 'int'}}
    point_schema = {'geometry': 'Point', 'properties': {u'ID': 'int'}}
    line_schema = {'geometry': 'LineString', 'properties': {u'ID': 'int'}}

    #Schemas que definen los archivos utilizados en el problema
    usos_schema = {'geometry': 'Polygon',
        'properties': {u'PERIMETER': 'float',
            u'MANEJO': 'float',
            u'APL': 'int',
            u'LABELID': 'float',
            u'AREA': 'float',
            u'OLD_RODAL': 'str:4',
            u'SUBRODAL': 'str:3',
            u'USOS_': 'float',
            u'RODAL': 'str:4',
            u'CLASEUSO': 'str:2',
            u'SECCION': 'str:2',
            u'USOS_ID': 'float',
            u'TIPOUSO': 'str:4',
            u'OLD_LABID': 'float',
            u'CODIGO': 'str:5',
            u'MPL': 'str:2'}}

    canchas_schema = {'geometry': 'Point',
        'properties': {u'FORMA': 'str:4',
            u'NUM_EST4': 'int',
            u'NUM_EST3': 'int',
            u'NUM_EST2': 'int',
            u'NUM_EST1': 'int',
            u'ID_CANCHA': 'int',
            u'SUPERVISOR': 'str:5',
            u'LARGO': 'int',
            u'EST_CONST': 'str:4',
            u'X_CENTRO': 'int',
            u'SUP_NOM': 'int',
            u'TIPO': 'str:4',
            u'Y_CENTRO': 'int',
            u'EST_AVANT': 'str:1',
            u'EST_AVANR': 'str:1',
            u'EST_MANT': 'str:4',
            u'EMS_RIPIO': 'str:12',
            u'CARPETA': 'str:4',
            u'CAR_OBJE': 'str:2',
            u'ANCHO': 'int',
            u'REQ_OBRA': 'str:2',
            u'EMS_TIERRA': 'str:12',
            u'FCH_AVANT': 'str:10',
            u'FCH_AVANR': 'str:10'}}

    caminos_schema = {'geometry': 'LineString',
        'properties': {u'TIPO_PROP': 'str:4',
            u'SUPERVISOR': 'str:5',
            u'GCAMINO': 'str:25',
            u'GCARPETA': 'str:25',
            u'EST_CONST': 'str:4',
            u'INTERVEN': 'str:10',
            u'ACT_FOTO': 'str:2',
            u'TIPO_CAM': 'str:2',
            u'TIPO_CAR': 'str:2',
            u'CODIGO': 'str:5',
            u'EST_AVANR': 'str:1',
            u'EST_AVANT': 'str:1',
            u'ID_ARCO': 'int',
            u'EST_MANT': 'str:4',
            u'EMS_RIPIO': 'str:12',
            u'ID_PREDIO': 'str:5',
            u'GPREDIO': 'str:30',
            u'CAR_OBJE': 'str:2',
            u'ANCHO': 'float',
            u'ID_CAMINO': 'int',
            u'REQ_OBRA': 'str:2',
            u'ANO_OFER': 'int',
            u'LENGTH': 'float',
            u'SECCION': 'str:2',
            u'EMS_TIERRA': 'str:12',
            u'FCH_AVANT': 'str:10',
            u'FCH_AVANR': 'str:10',
            u'LREAL': 'float'}}

    curvas_schema = {'geometry': 'LineString',
        'properties': {u'TNODE_': 'float',
            u'CURVAS_': 'float',
            u'RPOLY_': 'float',
            u'LPOLY_': 'float',
            u'CURVAS_ID': 'float',
            u'LENGTH': 'float',
            u'SECCION': 'str:2',
            u'GCURVA': 'str:25',
            u'FNODE_': 'float',
            u'NOMBRE': 'str:32',
            u'CODIGO': 'str:5',
            u'TIPO_CUR': 'int',
            u'COTA': 'int'}}

    hidro_schema = {'geometry': 'LineString',
        'properties': {u'TNODE_': 'float',
            u'ANCHO': 'float',
            u'RPOLY_': 'float',
            u'LPOLY_': 'float',
            u'TIPO_HID': 'int',
            u'HIDRO_ID': 'float',
            u'ID_LIN': 'float',
            u'HIDRO_': 'float',
            u'LENGTH': 'float',
            u'SECCION': 'str:2',
            u'GPREDIO': 'str:30',
            u'GHIDRO': 'str:25',
            u'FNODE_': 'float',
            u'PEND_PROM': 'float',
            u'CODIGO': 'str:5',
            u'ESTADO': 'str:30'}}

    pendi_schema = {'geometry': 'Polygon',
        'properties': {u'OBJECTID': 'int',
            u'ID_EMPRESA': 'str:1',
            u'ID_PREDIO': 'str:5',
            u'ID_AREA': 'str:2',
            u'RANGO': 'str:254',
            u'NOMBRE': 'str:24',
            u'CODIGO': 'str:5',
            u'SLOPE_CODE': 'float'}}

    escenario_schema = {'geometry': 'Polygon',
        'properties': {u'RESP_CP': 'str:3',
            u'PROD_23': 'float',
            u'PROD_22': 'float',
            u'PROD_21': 'float',
            u'PROD_20': 'float',
            u'PROD_25': 'float',
            u'PROD_24': 'float',
            u'ALTURA_200': 'float',
            u'DENS_FIN': 'int',
            u'DCM': 'float',
            u'FCH_INIFAE': 'date',
            u'AREA_BASAL': 'float',
            u'SESION': 'str:1',
            u'DESC_ERROR': 'str:50',
            u'FID_PLA__1': 'int',
            u'TIPO_EQUI': 'str:4',
            u'ID_PREDIO': 'str:5',
            u'NUM_EST': 'int',
            u'ID_EQUIPO': 'str:5',
            u'DENSIDAD_T': 'float',
            u'NUEVOUSO': 'str:4',
            u'PODADOS_TO': 'float',
            u'PROCAR': 'str:1',
            u'APL': 'int',
            u'MES_AVAN': 'str:2',
            u'FCH_VIGFIN': 'date',
            u'NEWMPL': 'str:2',
            u'ALTURA_POD': 'float',
            u'GLOSA': 'str:8',
            u'ID_PLANMA': 'str:9',
            u'SUBRODAL': 'str:3',
            u'FCH_VIGINI': 'date',
            u'CLASE': 'int',
            u'TIPO_CARPE': 'str:4',
            u'VOL_TOT_EX': 'float',
            u'HECTARES': 'float',
            u'TIPOUSO': 'str:4',
            u'MES_PO': 'str:2',
            u'ANO_AVAN': 'str:4',
            u'FCH_SOL_PM': 'date',
            u'FCH_AVAN': 'str:10',
            u'INCLUIDO': 'str:1',
            u'PROD_05': 'float',
            u'PROD_04': 'float',
            u'PROD_07': 'float',
            u'PROD_06': 'float',
            u'PROD_01': 'float',
            u'PROD_03': 'float',
            u'PROD_02': 'float',
            u'PROD_09': 'float',
            u'PROD_08': 'float',
            u'PLAN_PROD': 'str:4',
            u'ORDEN_CAM': 'str:12',
            u'TIPO_MAD': 'str:4',
            u'PLAN_OPER': 'str:4',
            u'CLAVE3': 'str:24',
            u'AREA': 'float',
            u'PROD_12': 'float',
            u'PROD_13': 'float',
            u'PROD_10': 'float',
            u'PROD_11': 'float',
            u'PROD_16': 'float',
            u'PROD_17': 'float',
            u'PROD_14': 'float',
            u'PROD_15': 'float',
            u'PROD_18': 'float',
            u'PROD_19': 'float',
            u'USOS_ID': 'float',
            u'VER': 'str:3',
            u'MATER_CAM': 'str:18',
            u'NEWUSO': 'str:4',
            u'MES_PP': 'str:2',
            u'EST_PM': 'str:2',
            u'NEWCLASE': 'str:2',
            u'NEWRODAL': 'str:4',
            u'TEMPORADA': 'str:6',
            u'ID_INVENTA': 'str:6',
            u'MPL': 'str:2',
            u'NOM_CLASE': 'str:25',
            u'NUM_ACTA': 'str:5',
            u'VOL_TOT_PO': 'float',
            u'RODAL': 'str:4',
            u'VOL_TOT_PU': 'float',
            u'FCH_INVENT': 'date',
            u'ORDEN_APRO': 'str:12',
            u'EST_FAE': 'str:1',
            u'ARCHIVO': 'str:10',
            u'VOL_TOT_AS': 'float',
            u'NEWAPL': 'int',
            u'ORDEN_FAB': 'str:12',
            u'STATUS': 'int',
            u'COD_BLOCK': 'str:1',
            u'SOL_PM': 'str:1',
            u'NEWSECCION': 'str:2',
            u'PERIMETER': 'float',
            u'ESC_ORIG': 'int',
            u'USR_SOL_PM': 'str:5',
            u'CLASEUSO': 'str:2',
            u'VOLARB': 'float',
            u'SECCION': 'str:2',
            u'FID_PLA_ES': 'int',
            u'PLANIFICA': 'str:1'}}

    #Schemas utilizados por el algoritmo
    scope_schema = {'geometry': 'Polygon',
        'properties': {u'FORMA': 'str:4',
            u'NUM_EST4': 'int',
            u'NUM_EST3': 'int',
            u'NUM_EST2': 'int',
            u'NUM_EST1': 'int',
            u'ID_CANCHA': 'int',
            u'SUPERVISOR': 'str:5',
            u'LARGO': 'int',
            u'EST_CONST': 'str:4',
            u'X_CENTRO': 'int',
            u'SUP_NOM': 'int',
            u'TIPO': 'str:4',
            u'Y_CENTRO': 'int',
            u'EST_AVANT': 'str:1',
            u'EST_AVANR': 'str:1',
            u'EST_MANT': 'str:4',
            u'EMS_RIPIO': 'str:12',
            u'CARPETA': 'str:4',
            u'CAR_OBJE': 'str:2',
            u'ANCHO': 'int',
            u'REQ_OBRA': 'str:2',
            u'EMS_TIERRA': 'str:12',
            u'FCH_AVANT': 'str:10',
            u'FCH_AVANR': 'str:10'}}

    slope_equi_schema = {'geometry': 'MultiPolygon',
        'properties': {u'TIPO': 'str:4',
            u'SLOPE_CODE': 'int'}}

    contour_schema = {'geometry': 'MultiPolygon',
        'properties': {u'TIPO': 'str:4'}}

    usos_generados_schema = {'geometry': 'MultiPolygon',
        'properties': {u'TIPO': 'str:4',
            u'EQUIPO': 'str:4'}}

    def __init__(self, usos_schema=None):
        if usos_schema is not None:
            self.usos_schema = usos_schema