# -*- coding: utf-8 -*-

def classFactory(iface):
    from .road_inspection_viewer import road_inspection_viewer
    return road_inspection_viewer(iface)
