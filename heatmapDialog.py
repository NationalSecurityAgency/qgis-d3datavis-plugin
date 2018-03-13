import os
import re
import dateutil.parser
import webbrowser
from shutil import copyfile

from qgis.PyQt import uic
from qgis.PyQt.QtCore import QSettings, QVariant, QUrl, QTime, QDateTime, QDate
from qgis.PyQt.QtWidgets import QDialog, QFileDialog, QMessageBox, QDialogButtonBox

from qgis.core import Qgis, QgsMapLayerProxyModel, QgsFieldProxyModel, QgsVectorLayer, QgsFeatureRequest
from qgis.gui import QgsColorButton

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'heatmapdialog.ui'))

OPTIONMENU = ['Year', 'Month', 'Day of Month', 'Day of Week', 'Hour of Day', 'Custom Category Field']

class AutoDict(dict):
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] =  type(self)()
        return value
    def __iadd__(self, item):
        return item
        
class HeatmapDialog(QDialog, FORM_CLASS):
    CUSTOM_TYPES = [QVariant.String, QVariant.Int, QVariant.UInt, QVariant.LongLong, QVariant.ULongLong]
    def __init__(self, iface, parent):
        """ Constructor to initialize the circular heatmap dialog box """
        super(HeatmapDialog, self).__init__(parent)
        self.setupUi(self)
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.layerComboBox.setFilters(QgsMapLayerProxyModel.VectorLayer)
        self.layerComboBox.layerChanged.connect(self.userSelectsLayer)
        self.dtComboBox.setFilters(QgsFieldProxyModel.String | QgsFieldProxyModel.Date | QgsFieldProxyModel.Time)
        self.dateComboBox.setFilters(QgsFieldProxyModel.String | QgsFieldProxyModel.Date)
        self.timeComboBox.setFilters(QgsFieldProxyModel.String | QgsFieldProxyModel.Time)
        self.categoryComboBox.setFilters(QgsFieldProxyModel.String | QgsFieldProxyModel.Numeric)
        self.dtRadioButton.clicked.connect(self.enableComponents)
        self.notdtRadioButton.clicked.connect(self.enableComponents)
        self.radialComboBox.addItems(OPTIONMENU)
        self.circleComboBox.addItems(OPTIONMENU)
        self.buttonBox.button(QDialogButtonBox.Ok).setText("Create Chart")
        self.buttonBox.button(QDialogButtonBox.Help).clicked.connect(self.help)

    def help(self):
        url = QUrl.fromLocalFile(os.path.dirname(__file__) + "/index.html").toString()
        webbrowser.open(url, new=2)
        
    def showEvent(self, event):
        """When the heatmap dialog box is displayed, preinitialize it and populate
           it with all the vector layers"""
        super(HeatmapDialog, self).showEvent(event)
        self.initLayerFields()
    
    def userSelectsLayer(self):
        """The user has selected a layer so we need to initialize the layer field combo boxes"""
        self.initLayerFields()
        
    def initLayerFields(self):
        """ Initialize the following combo boxes: dtComboBox, dateComboBox, and timeComboBox. """
        layer = self.layerComboBox.currentLayer()
        self.categoryComboBox.setLayer(layer)
        self.dtComboBox.setLayer(layer)
        self.dateComboBox.setLayer(layer)
        self.timeComboBox.setLayer(layer)
        self.dtRadioButton.setChecked(True)
        self.enableComponents()
    
    def enableComponents(self):
        # Based on selections enable or disable certain radio buttons and combo boxes
        if self.dtRadioButton.isChecked():
            self.dtComboBox.setEnabled(True)
            self.dateComboBox.setEnabled(False)
            self.timeComboBox.setEnabled(False)
        else:
            self.dtComboBox.setEnabled(False)
            self.dateComboBox.setEnabled(True)
            self.timeComboBox.setEnabled(True)
        
    def readChartParams(self):
        """ Read all the parameters from the GUI that we need to generate a chart. """
        self.selectedLayer = self.layerComboBox.currentLayer()
        self.selectedDateTimeCol = self.selectedLayer.fields().lookupField(self.dtComboBox.currentField())
        self.selectedDateCol = self.selectedLayer.fields().lookupField(self.dateComboBox.currentField())
        self.selectedTimeCol = self.selectedLayer.fields().lookupField(self.timeComboBox.currentField())
        self.selectedRadialUnit = self.radialComboBox.currentIndex()
        self.selectedCircleUnit = self.circleComboBox.currentIndex()
        self.customFieldCol = -1
        if self.selectedRadialUnit == 5 or self.selectedCircleUnit == 5:
            if self.categoryComboBox.count() > 0:
                self.customFieldCol = self.selectedLayer.fields().lookupField(self.categoryComboBox.currentField())
        self.showRadialLabels = self.radialLabelCheckBox.isChecked()
        self.showBandLabels = self.bandLabelCheckBox.isChecked()
        self.showLegend = self.legendCheckBox.isChecked()
        self.chartTitle = str(self.titleEdit.text())
        self.legendTitle = str(self.legendEdit.text())
        self.showDataValues = self.showValuesCheckBox.isChecked()
        self.dataValueLabel = str(self.dataValueLabelEdit.text())
        try:
            self.chartInnerRadius = int(self.innerRadiusEdit.text())
        except:
            # Need a valid exception error
            self.chartInnerRadius = 25
            self.innerRadiusEdit.setText('25') # Set it to the default value
        try:
            self.chartBandHeight = int(self.bandHeightEdit.text())
        except:
            self.chartBandHeight = 16
            self.bandHeightEdit.setText('16')
        # Legend Settings
        try: # Legend Height
            self.legendHeight = int(self.legendHeightEdit.text())
        except:
            self.legendHeight = 300
            self.legendHeightEdit.setText('300')
        try: # Legend Width
            self.legendWidth = int(self.legendWidthEdit.text())
        except:
            self.legendWidth = 30
            self.legendWidthEdit.setText('30')
        try: # Legend Box Width
            self.legendBoxWidth = int(self.legendBoxWidthEdit.text())
        except:
            self.legendBoxWidth = 200
            self.legendBoxWidthEdit.setText('200')
        self.beginningColor = self.startColor.color().name()
        self.endingColor = self.endColor.color().name()
        self.noDataColor = self.noDataColorSelector.color().name()

    def parseDateTimeValues(self, requestedField, dt, time):
        '''This returns the requested date or time value from a datetime
           date only and/or time only field. Note that it can throw an exception.'''
        
        if requestedField == 4:
            # We are only interested in the hour of the day
            if isinstance(time, QTime):
                return time.hour()
            elif isinstance(time, QDateTime):
                return time.time().hour()
            else: # Parse it as a string
                d = dateutil.parser.parse(time)
                return d.hour
        elif isinstance(dt, QDate):
            if requestedField == 0: # Year
                return dt.year()
            elif requestedField == 1: # Month
                return dt.month()
            elif requestedField == 2: # Day
                return dt.day()
            elif requestedField == 3: # Day of Week
                return dt.dayOfWeek() - 1
        elif isinstance(dt, QDateTime):
            if requestedField == 0: # Year
                return dt.date().year()
            elif requestedField == 1: # Month
                return dt.date().month()
            elif requestedField == 2: # Day
                return dt.date().day()
            elif requestedField == 3: # Day of Week
                return dt.date().dayOfWeek() - 1        
        else: # Parse as a string
            d = dateutil.parser.parse(dt)
            if requestedField == 0:
                return d.year
            elif requestedField == 1:
                return d.month
            elif requestedField == 2:
                return d.day
            elif requestedField == 3:
                return d.weekday()
        
        raise ValueError('The only supported data types are QString, QDateTime, QDate, and QTime')
                    
    def accept(self):
        """ This is called when the user has clicked on the "OK" button to create the chart."""
        if self.layerComboBox.count() == 0:
            return
        self.readChartParams()
        uniqueCustomFields = []
        if self.selectedRadialUnit == 5 or self.selectedCircleUnit == 5:
            if self.customFieldCol == -1:
                self.iface.messageBar().pushMessage("", "Custom Category Filed cannot be selected because none is selected" , level=Qgis.Warning, duration=3)
                return
            uniqueCustomFields = self.selectedLayer.uniqueValues(self.customFieldCol)
            if len(uniqueCustomFields) > 40:
                # We have too many categories
                self.iface.messageBar().pushMessage("", "There are too many custom categories for a chart" , level=Qgis.Warning, duration=3)
                return;
        folder = askForFolder(self)
        if not folder:
            return
        
        # Set aside some space to accumulate the statistics
        data   = AutoDict()
        rvlist = AutoDict()
        cvlist = AutoDict()
        request = QgsFeatureRequest().setFlags(QgsFeatureRequest.NoGeometry)
        isdt = self.dtRadioButton.isChecked()
        attributes = []
        if isdt:
            attributes.append(self.selectedDateTimeCol)
        else:
            attributes.extend([self.selectedDateCol, self.selectedTimeCol])
        if self.customFieldCol != -1:
            attributes.append(self.customFieldCol)
        
        request.setSubsetOfAttributes(attributes)
        
        if isdt:
            col1 = self.selectedDateTimeCol
            col2 = self.selectedDateTimeCol
        else:
            col1 = self.selectedDateCol
            col2 = self.selectedTimeCol
        
        # Iterate through each feature and parse and process the date/time values
        iter = self.selectedLayer.getFeatures(request)
        for f in iter:
            try:
                if self.selectedRadialUnit == 5:
                    rv = f[self.customFieldCol]
                    if rv == None:
                        continue
                else:
                    rv = self.parseDateTimeValues(self.selectedRadialUnit, f[col1], f[col2])
                if self.selectedCircleUnit == 5:
                    cv = f[self.customFieldCol]
                    if cv == None:
                        continue
                else:
                    cv = self.parseDateTimeValues(self.selectedCircleUnit, f[col1], f[col2])
            except:
                continue
            
            rvlist[rv] += 1
            cvlist[cv] += 1
            data[rv][cv] += 1
        if not any(cvlist) or not any(rvlist):
            self.iface.messageBar().pushMessage("", "Valid dates were not found" , level=Qgis.Warning, duration=3)
            return
        rvrange, segCnt, rvunits = self.getUnitStr(rvlist, self.selectedRadialUnit)
        cvrange, bandCnt, cvunits = self.getUnitStr(cvlist, self.selectedCircleUnit)
        if rvunits is None or cvunits is None:
            self.iface.messageBar().pushMessage("", "There is too large of a year range to create chart" , level=Qgis.Warning, duration=3)
            return
        
        # Create the web page with all the JavaScript variables
        datastr = self.formatData(data, rvrange, cvrange)
        
        chartSize = self.chartInnerRadius*2 + (bandCnt + 1)*2*self.chartBandHeight + 10 # 10 is additional margin
        style = (".legendContainer {{\n"
                 "	height: {};\n"
                 "}}\n"
                 ".legend svg {{\n"
                 "	width: {}px;\n"
                 "	height: {}px;\n"
                 "}}\n"
                 "#chart svg {{\n"
                 "	height: {}px;\n"
                 "	width: {}px;\n"
                 "}}\n"
                ).format(chartSize, self.legendBoxWidth, self.legendHeight, chartSize, chartSize)

        script = []
        script.append('var segHeight={};'.format(self.chartBandHeight))
        script.append('var segCnt={};'.format(segCnt))
        script.append('var bandCnt={};'.format(bandCnt))
        script.append('var segLabels={};'.format(rvunits))
        script.append('var bandLabels={};'.format(cvunits))
        script.append('var innerRadius={};'.format(self.chartInnerRadius))
        script.append('var edata=[{}];'.format(datastr))
        script.append('var startColor="{}";'.format(self.beginningColor))
        script.append('var endColor="{}";'.format(self.endingColor))
        script.append('var noDataColor="{}";'.format(self.noDataColor))
        rl = ''
        if self.showRadialLabels:
            rl = '\n\t.segmentLabels(segLabels)'
        bl = ''
        if self.showBandLabels:
            bl = '\n\t.radialLabels(bandLabels)'
        ll = ''
        if self.showLegend:
            ll = '\n\t.legDivId("legend")\n\t.legendSettings({{width: {}, height: {}, legBlockWidth: {}}})\n\t.data(edata)\n'.format(self.legendBoxWidth, self.legendHeight, self.legendWidth)
        script.append('var chart = circularHeatChart()\n\t.range([startColor,endColor])\n\t.nullColor(noDataColor)\n\t.segmentHeight(segHeight)\n\t.innerRadius(innerRadius)\n\t.numSegments(segCnt){}{}{};'
                .format(rl, bl, ll))
        script.append('d3.select(\'#chart\')\n\t.selectAll(\'svg\')\n\t.data([edata])\n\t.enter()\n\t.append(\'svg\')\n\t.call(chart);')
        
        if self.showDataValues:
            script.append('d3.selectAll("#chart path").on(\'mouseover\', function() {\n\tvar d = d3.select(this).data();\n\td3.select("#info").text(\'' +
                self.dataValueLabel + ' \' + d);\n});')
                
        if self.showLegend:
            script.append('d3.select("#legendTitle").html("' + str(self.legendEdit.text()).replace('"', '\\"') + '");\n')

        values = {"@TITLE@": self.chartTitle,
                "@STYLE@": style,
                "@SCRIPT@": '\n'.join(script)
            }
        template = os.path.join(os.path.dirname(__file__), "templates", "index.html")
        html = replaceInTemplate(template, values)
        
        filename = os.path.join(folder, "index.html")
        try:
            fout = open(filename, 'w')
        except:
            self.iface.messageBar().pushMessage("", "Error opening output file" , level=Qgis.Critical, duration=3)
            return
        fout.write(html)
        fout.close()
        #Copy over the d3 libraries
        copyfile(os.path.join(os.path.dirname(__file__), "d3", "d3.min.js"), 
            os.path.join(folder,"d3.min.js"))
        copyfile(os.path.join(os.path.dirname(__file__), "d3", "circularHeatChart.js"), 
            os.path.join(folder,"circularHeatChart.js"))
        # open the web browser
        url = QUrl.fromLocalFile(filename).toString()
        webbrowser.open(url, new=2) # new=2 is a new tab if possible
        QMessageBox().information(self, "Date Time Heatmap", "Chart has been created")
        
    
    def formatData(self, data, rvrange, cvrange):
        """This create the Javascript string of data"""
        datastrs=[]
        for x in cvrange:
            for y in rvrange:
                if not data[y][x]:
                    datastrs.append('null')
                else:
                    datastrs.append(str(data[y][x]))
        return ','.join(datastrs)
        
    
    def getUnitStr(self, ulist, unit):
        """ This creates the string of unit labels that will be used by the web page chart"""
        if unit == 0:
            minval = min(ulist)
            maxval = max(ulist)
            if (maxval - minval) > 40:
                return -1, -1, None
            cnt = maxval - minval + 1-12
            urange = list(range(minval, maxval + 1))
            years = ['%d'%x for x in urange]
            labels = '["'+'","'.join(years)+'"]'
            
        elif unit == 1: # Months 1-12
            cnt = 12
            urange = list(range(1,13))
            labels =  '["January","February","March","April","May","June","July","August","September","October","November","December"]'
        elif unit == 2: # Days of the month - possible 1 - 31
            cnt = 31
            urange = list(range(1,32))
            labels = '["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20","21","22","23","24","25","26","27","28","29","30","31"]'
        elif unit == 3: # Days of the week 0 - 6
            cnt = 7
            urange = list(range(0,7))
            labels = '["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]'
        elif unit == 4: # Hours of the day 0-23
            cnt = 24
            urange = list(range(0,24))
            labels = '["Midnight", "1am", "2am", "3am", "4am", "5am", "6am", "7am", "8am", "9am", "10am", "11am", "Noon", "1pm", "2pm", "3pm", "4pm", "5pm", "6pm", "7pm", "8pm", "9pm", "10pm", "11pm"]'
        else:
            urange = sorted(ulist.keys())
            labels = []
            cnt = len(urange)
            for item in urange:
                labels.append(str(item))
        return urange, cnt, labels

def replaceInTemplate(template, values):
    """ This merges the values into the template to create the output web page """
    path = os.path.join(os.path.dirname(__file__), "templates", template)
    with open(path) as f:
        lines = f.readlines()
    s = "".join(lines)
    for name,value in values.items():
        s = s.replace(name, value)
    return s
    
"""
The following keep track of and saves the last folder used by the get directory
dialog box.
"""

LAST_PATH = "LastPath"

def askForFolder(parent, name="HeatmapPath"):
    path = getSetting(LAST_PATH, name)
    folder =  QFileDialog.getExistingDirectory(parent, "Select folder to store chart", path)
    if folder:
        setSetting(LAST_PATH, name, folder)
    return folder


def setSetting(namespace, name, value):
    settings = QSettings()
    settings.setValue(namespace + "/" + name, value)

def getSetting(namespace, name):
    v = QSettings().value(namespace + "/" + name, None)
    return v