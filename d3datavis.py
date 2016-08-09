from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

# Initialize Qt resources from file resources.py
import resources

import os.path
from heatmapDialog import HeatmapDialog



class D3DataVis:
    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        """ Initialize the menu and dialog boxes for the D3 heatmap chart """
        self.heatmapDialog = HeatmapDialog(self.iface, self.iface.mainWindow())
        icon = QIcon(":/plugins/d3datavis/icon.png")
        self.heatmapAction = QAction(icon, u"Circular Date/Time Heatmap", self.iface.mainWindow())
        self.heatmapAction.triggered.connect(self.showHeatmapDialog)
        self.heatmapAction.setCheckable(False)
        self.iface.addToolBarIcon(self.heatmapAction)
        # Add a D3 Data Visualization menu item to the Web menu
        self.iface.addPluginToWebMenu(u"D3 Data Visualization", self.heatmapAction)

    def unload(self):
        self.iface.removePluginWebMenu(u"D3 Data Visualization", self.heatmapAction)
        self.iface.removeToolBarIcon(self.heatmapAction)
    
    def showHeatmapDialog(self):
        """Display the circular date/time heatmap dialog box"""
        self.heatmapDialog.show()
        
        
