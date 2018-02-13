from PyQt4.QtGui import QIcon, QAction

import os.path

class D3DataVis:
    heatmapDialog = None
    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        """ Initialize the menu and dialog boxes for the D3 heatmap chart """
        icon = QIcon(os.path.dirname(__file__) + "/icon.png")
        self.heatmapAction = QAction(icon, u"Circular Date/Time Heatmap", self.iface.mainWindow())
        self.heatmapAction.triggered.connect(self.showHeatmapDialog)
        self.heatmapAction.setCheckable(False)
        self.iface.addWebToolBarIcon(self.heatmapAction)
        # Add a D3 Data Visualization menu item to the Web menu
        self.iface.addPluginToWebMenu(u"D3 Data Visualization", self.heatmapAction)

    def unload(self):
        self.iface.removePluginWebMenu(u"D3 Data Visualization", self.heatmapAction)
        self.iface.removeWebToolBarIcon(self.heatmapAction)
    
    def showHeatmapDialog(self):
        """Display the circular date/time heatmap dialog box"""
        if not self.heatmapDialog:
            from .heatmapDialog import HeatmapDialog
            self.heatmapDialog = HeatmapDialog(self.iface, self.iface.mainWindow())
        self.heatmapDialog.show()
        
        
