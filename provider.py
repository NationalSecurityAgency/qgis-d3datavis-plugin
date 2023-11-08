"""
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
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
