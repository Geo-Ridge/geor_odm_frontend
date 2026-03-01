# -*- coding: utf-8 -*-
"""ODM Frontend QGIS Plugin."""
import os
from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import Qt

from .ui.main_dialog import ODMMainDialog
from .resources import resources_rc

class ODMPlugin:
    """Main plugin class."""

    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.action = None
        self.dock = None

    def initGui(self):
        """Initialize plugin GUI."""
        self.action = QAction(
            QIcon(":/plugins/odm_frontend/drone.svg"),
            'ODM Frontend',
            self.iface.mainWindow()
        )
        self.action.triggered.connect(self.run)
        self.iface.addPluginToMenu('ODM Frontend', self.action)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        """Unload plugin."""
        self.iface.removePluginMenu('ODM Frontend', self.action)
        self.iface.removeToolBarIcon(self.action)
        if self.dock:
            if hasattr(self.dock, 'photos_dock') and self.dock.photos_dock:
                self.iface.removeDockWidget(self.dock.photos_dock)
            self.iface.removeDockWidget(self.dock)

    def run(self):
        """Toggle dock visibility."""
        if self.dock is None:
            self.dock = ODMMainDialog(self.iface)
            self.dock.setObjectName('odm_main_dock')
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dock)
        else:
            if self.dock.isVisible():
                self.dock.hide()
                if hasattr(self.dock, 'photos_dock') and self.dock.photos_dock:
                    self.dock.photos_dock.hide()
            else:
                self.dock.show()
