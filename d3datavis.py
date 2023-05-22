import os
from qgis.core import QgsApplication
from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
import processing

try:
    from wordcloud import WordCloud
    import matplotlib.pyplot as plt
    has_wordcloud = True
except Exception:
    has_wordcloud = False

from .provider import DataVisProvider

class D3DataVis:
    heatmapDialog = None
    def __init__(self, iface):
        self.iface = iface
        self.provider = DataVisProvider()

    def initGui(self):
        """ Initialize the menu and dialog boxes for the D3 heatmap chart """
        self.toolbar = self.iface.addToolBar('Data Visualization Toolbar')
        self.toolbar.setObjectName('DataVisToolbar')
        self.toolbar.setToolTip('Data Visualization Toolbar')

        icon = QIcon(os.path.dirname(__file__) + "/icons/icon.png")
        self.heatmapAction = QAction(icon, "Circular Date/Time Heatmap", self.iface.mainWindow())
        self.heatmapAction.triggered.connect(self.showHeatmapDialog)
        self.iface.addPluginToWebMenu("D3 Data Visualization", self.heatmapAction)
        self.toolbar.addAction(self.heatmapAction)
        
        if has_wordcloud:
            icon = QIcon(os.path.dirname(__file__) + "/icons/wordcloud.svg")
            self.wordCloudAction = QAction(icon, "Word cloud from attribute", self.iface.mainWindow())
            self.wordCloudAction.triggered.connect(self.wordCloud)
            self.iface.addPluginToWebMenu("D3 Data Visualization", self.wordCloudAction)
            self.toolbar.addAction(self.wordCloudAction)
            icon = QIcon(os.path.dirname(__file__) + "/icons/wordcloudfile.svg")
            self.wordCloudFileAction = QAction(icon, "Word cloud from file", self.iface.mainWindow())
            self.wordCloudFileAction.triggered.connect(self.wordCloudFile)
            self.iface.addPluginToWebMenu("D3 Data Visualization", self.wordCloudFileAction)
            self.toolbar.addAction(self.wordCloudFileAction)

            # Add the processing provider
            QgsApplication.processingRegistry().addProvider(self.provider)

        # Help
        icon = QIcon(os.path.dirname(__file__) + '/icons/help.svg')
        self.helpAction = QAction(icon, "Help", self.iface.mainWindow())
        self.helpAction.triggered.connect(self.help)
        self.iface.addPluginToWebMenu('D3 Data Visualization', self.helpAction)

    def unload(self):
        self.iface.removePluginWebMenu("D3 Data Visualization", self.heatmapAction)
        self.iface.removeToolBarIcon(self.heatmapAction)
        if has_wordcloud:
            self.iface.removePluginWebMenu("D3 Data Visualization", self.wordCloudAction)
            self.iface.removeToolBarIcon(self.wordCloudAction)
            self.iface.removePluginWebMenu("D3 Data Visualization", self.wordCloudFileAction)
            self.iface.removeToolBarIcon(self.wordCloudFileAction)
            QgsApplication.processingRegistry().removeProvider(self.provider)
        self.iface.removePluginWebMenu('D3 Data Visualization', self.helpAction)
        del self.toolbar
    
    def showHeatmapDialog(self):
        """Display the circular date/time heatmap dialog box"""
        if not self.heatmapDialog:
            from .heatmapDialog import HeatmapDialog
            self.heatmapDialog = HeatmapDialog(self.iface, self.iface.mainWindow())
        self.heatmapDialog.show()

    def wordCloud(self):
        processing.execAlgorithmDialog('datavis:wordcloud', {})

    def wordCloudFile(self):
        processing.execAlgorithmDialog('datavis:filewordcloud', {})

    def help(self):
        '''Display a help page'''
        import webbrowser
        url = QUrl.fromLocalFile(os.path.dirname(__file__) + "/index.html").toString()
        webbrowser.open(url, new=2)
