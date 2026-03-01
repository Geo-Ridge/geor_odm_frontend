# -*- coding: utf-8 -*-
"""QGIS ODM Frontend Plugin - Refactored Version

A clean, modular QGIS plugin for OpenDroneMap processing.
"""

def classFactory(iface):
    from .plugin import ODMPlugin
    return ODMPlugin(iface)
