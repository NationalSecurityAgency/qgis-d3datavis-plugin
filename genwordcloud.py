import os

from qgis.PyQt.uic import loadUiType
from qgis.PyQt.QtWidgets import QDialog
from qgis.core import Qgis, QgsFieldProxyModel, QgsMapLayerProxyModel
from qgis.gui import QgsFileWidget

from wordcloud import WordCloud
import matplotlib.pyplot as plt

FORM_CLASS, _ = loadUiType(os.path.join(
    os.path.dirname(__file__), 'wordcloud.ui'))
        
class WordCloudDialog(QDialog, FORM_CLASS):
    def __init__(self, iface, parent):
        """ Constructor to initialize the word cloud dialog box """
        super(WordCloudDialog, self).__init__(parent)
        self.setupUi(self)
        self.iface = iface
        self.layerComboBox.layerChanged.connect(self.layerChanged)
        self.layerComboBox.setFilters(QgsMapLayerProxyModel.VectorLayer)
        self.attrFieldComboBox.setFilters(QgsFieldProxyModel.String)
        self.font_path = os.path.join(os.path.dirname(__file__), 'font/DroidSansMono.ttf')
        self.outputFileWidget.setStorageMode(QgsFileWidget.SaveFile)
        self.outputFileWidget.setFilter('*.png')

    def showEvent(self, e):
        self.layerChanged()

    def layerChanged(self):
        if not self.isVisible():
            return
        layer = self.layerComboBox.currentLayer()
        self.attrFieldComboBox.setLayer(layer)
            
    def accept(self):
        if self.layerComboBox.count() == 0:
            return
        layer = self.layerComboBox.currentLayer()
        field_col = layer.fields().lookupField(self.attrFieldComboBox.currentField())
        if field_col == -1:
            self.iface.messageBar().pushMessage("", "No string field available", level=Qgis.Warning, duration=3)
            return
        output_image = self.outputFileWidget.filePath()
        width = self.widthSpinBox.value()
        height = self.heightSpinBox.value()
        max_words = self.maxWordsSpinBox.value()
        min_font_size = self.minFontSpinBox.value()
        max_font_size = self.maxFontSpinBox.value()
        if max_font_size == 0:
            max_font_size = None
        min_word_length = self.minWordLengthSpinBox.value()
        transparent = self.transparentCheckBox.isChecked()
        if transparent:
            background_color = None
            mode = 'RGBA'
        else:
            background_color = self.backgroundLineEdit.text().strip()
            mode = 'RGB'
        
        lines = []
        iter = layer.getFeatures()
        for f in iter:
            s = f[field_col]
            if s:
                s = s.strip()
                if s:
                    lines.append(s)
        text = ', '.join(lines)
        wordcloud = WordCloud(font_path=self.font_path, width=width, height=height, min_font_size=min_font_size,
            max_font_size=max_font_size, max_words=max_words, min_word_length=min_word_length,
            background_color=background_color, mode=mode).generate(text)
        if output_image:
            image = wordcloud.to_image()
            image.save(output_image)
        else:
            plt.figure()
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis("off")
            plt.show()

