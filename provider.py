import os
from qgis.core import QgsProcessingProvider
from qgis.PyQt.QtGui import QIcon
from .genwordcloud import WordCloudAlgorithm
from .filewordcloud import FileWordCloudAlgorithm

class DataVisProvider(QgsProcessingProvider):

    def unload(self):
        QgsProcessingProvider.unload(self)

    def loadAlgorithms(self):
        self.addAlgorithm(WordCloudAlgorithm())
        self.addAlgorithm(FileWordCloudAlgorithm())

    def icon(self):
        return QIcon(os.path.dirname(__file__) + '/icons/wordcloud.svg')

    def id(self):
        return 'datavis'

    def name(self):
        return 'Data Visualization'

    def longName(self):
        return self.name()
