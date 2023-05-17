from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

try:
    from wordcloud import WordCloud
    import matplotlib.pyplot as plt
    has_wordcloud = True
except Exception:
    has_wordcloud = False


import os.path

class D3DataVis:
    heatmapDialog = None
    wordcloudDialog = None
    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        """ Initialize the menu and dialog boxes for the D3 heatmap chart """
        icon = QIcon(os.path.dirname(__file__) + "/icon.png")
        self.heatmapAction = QAction(icon, "Circular Date/Time Heatmap", self.iface.mainWindow())
        self.heatmapAction.triggered.connect(self.showHeatmapDialog)
        self.iface.addPluginToWebMenu("D3 Data Visualization", self.heatmapAction)
        self.iface.addWebToolBarIcon(self.heatmapAction)
        
        if has_wordcloud:
            icon = QIcon(os.path.dirname(__file__) + "/wordcloud.png")
            self.wordCloudAction = QAction(icon, "Generate Word Cloud", self.iface.mainWindow())
            self.wordCloudAction.triggered.connect(self.showWordCloudDialog)
            self.iface.addPluginToWebMenu("D3 Data Visualization", self.wordCloudAction)
            self.iface.addWebToolBarIcon(self.wordCloudAction)

    def unload(self):
        self.iface.removePluginWebMenu("D3 Data Visualization", self.heatmapAction)
        self.iface.removeWebToolBarIcon(self.heatmapAction)
        if has_wordcloud:
            self.iface.removePluginWebMenu("D3 Data Visualization", self.wordCloudAction)
            self.iface.removeWebToolBarIcon(self.wordCloudAction)
    
    def showHeatmapDialog(self):
        """Display the circular date/time heatmap dialog box"""
        if not self.heatmapDialog:
            from .heatmapDialog import HeatmapDialog
            self.heatmapDialog = HeatmapDialog(self.iface, self.iface.mainWindow())
        self.heatmapDialog.show()
    
    def showWordCloudDialog(self):
        if not self.wordcloudDialog:
            from .genwordcloud import WordCloudDialog
            self.wordcloudDialog = WordCloudDialog(self.iface, self.iface.mainWindow())
        self.wordcloudDialog.show()
        
        
