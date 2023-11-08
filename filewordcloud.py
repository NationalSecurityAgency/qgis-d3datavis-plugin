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
from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtGui import QIcon

from qgis.core import (
    QgsProcessing,
    QgsProcessingException,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFile,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterColor,
    QgsProcessingParameterNumber,
    QgsProcessingParameterFileDestination,
    QgsProcessingParameterField)

from wordcloud import WordCloud

class FileWordCloudAlgorithm(QgsProcessingAlgorithm):

    def initAlgorithm(self, config):
        self.addParameter(
            QgsProcessingParameterFile('INPUT', 'Input TXT file', extension='txt')
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                'WIDTH',
                'Output image width',
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=500
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                'HEIGHT',
                'Output image height',
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=500
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                'MAX_WORDS',
                'Maximum number of words',
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=200
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                'MIN_FONT',
                'Minimum font size',
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=4
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                'MAX_FONT',
                'Maximum font size (0 = Automatic sizing)',
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=0
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                'MIN_WORD_LEN',
                'Minimum word length',
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=0
            )
        )
        self.addParameter(
            QgsProcessingParameterColor(
                'BACKGROUND',
                'Background color',
                defaultValue='#000000'
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean (
                'TRANSPARENT',
                'Use transparent background',
                False,
                optional=False)
        )
        self.addParameter(
            QgsProcessingParameterFileDestination(
                'OUTPUT',
                'Output word clould image',
                fileFilter='Word cloud files (*.png *.tif *.svg)')
        )

    def processAlgorithm(self, parameters, context, feedback):
        output = self.parameterAsFileOutput(parameters, 'OUTPUT', context)
        input = self.parameterAsFile(parameters, 'INPUT', context)
        width = self.parameterAsInt(parameters, 'WIDTH', context)
        height = self.parameterAsInt(parameters, 'HEIGHT', context)
        max_words = self.parameterAsInt(parameters, 'MAX_WORDS', context)
        min_font_size = self.parameterAsInt(parameters, 'MIN_FONT', context)
        max_font_size = self.parameterAsInt(parameters, 'MAX_FONT', context)
        if max_font_size == 0:
            max_font_size = None
        min_word_length = self.parameterAsInt(parameters, 'MIN_WORD_LEN', context)
        transparent = self.parameterAsBoolean(parameters, 'TRANSPARENT', context)
        if transparent:
            bg_color = None
            mode = 'RGBA'
        else:
            bg_color = self.parameterAsColor(parameters, 'BACKGROUND', context).name()
            mode = 'RGB'

        try:
            text = open(input, 'r').read()
        except Exception:
            raise QgsProcessingException('Could not open input file')

        wordcloud = WordCloud(width=width, height=height, min_font_size=min_font_size,
            max_font_size=max_font_size, max_words=max_words, min_word_length=min_word_length,
            background_color=bg_color, mode=mode).generate(text)

        if output.lower().endswith('.svg'):
            try:
                wordcloud_svg = wordcloud.to_svg(embed_font=True)
                f = open(output,"w")
                f.write(wordcloud_svg)
                f.close()
            except Exception:
                pass
        else:
            image = wordcloud.to_image()
            image.save(output)

        return({})

    def name(self):
        return 'filewordcloud'

    def icon(self):
        return QIcon(os.path.dirname(__file__) + '/icons/wordcloudfile.svg')

    def displayName(self):
        return 'Word cloud from file'

    def helpUrl(self):
        file = os.path.dirname(__file__) + '/index.html'
        if not os.path.exists(file):
            return ''
        return QUrl.fromLocalFile(file).toString(QUrl.FullyEncoded)

    def createInstance(self):
        return FileWordCloudAlgorithm()
