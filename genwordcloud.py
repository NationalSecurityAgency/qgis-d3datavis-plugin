import os

from qgis.PyQt.uic import loadUiType
from qgis.PyQt.QtWidgets import QDialog
from qgis.core import QgsFieldProxyModel, QgsMapLayerProxyModel

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
            return
        width = self.widthSpinBox.value()
        height = self.heightSpinBox.value()
        max_words = self.maxWordsSpinBox.value()
        min_font_size = self.minFontSpinBox.value()
        max_font_size = self.maxFontSpinBox.value()
        if max_font_size == 0:
            max_font_size = None
        min_word_length = self.minWordLengthSpinBox.value()
        background_color = self.backgroundLineEdit.text().strip()
        
        lines = []
        iter = layer.getFeatures()
        for f in iter:
            s = f[field_col]
            if s:
                s = s.strip()
                if s:
                    lines.append(s)
        text = ' '.join(lines)
        wordcloud = WordCloud(font_path=self.font_path, width=width, height=height, min_font_size=min_font_size,
            max_font_size=max_font_size, max_words=max_words, min_word_length=min_word_length,
            background_color=background_color).generate(text)
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.show()

