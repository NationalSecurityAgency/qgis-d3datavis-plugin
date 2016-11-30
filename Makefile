PLUGINNAME = d3datavis
PY_FILES = d3datavis.py __init__.py heatmapDialog.py
EXTRAS = icon.png metadata.txt
UI_FILES = heatmapdialog.ui
TEMPLATES = templates/index.html
D3 = d3/d3.min.js d3/circularHeatChart.js

default: compile

compile: $(UI_FILES) $(RESOURCE_FILES)

deploy: compile
	mkdir -p $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)
	cp -vf $(PY_FILES) $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)
	cp -vf $(UI_FILES) $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)
	cp -vf $(EXTRAS) $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)
	mkdir -p $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)/templates/
	cp -vf $(TEMPLATES) $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)/templates/
	mkdir -p $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)/d3/
	cp -vf $(D3) $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)/d3/
	cp -vfr help $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)
	cp -vf helphead.html $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)/index.html
	python -m markdown -x markdown.extensions.headerid README.md >> $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)/index.html
	echo '</body>' >> $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)/index.html


clean:
	rm $(RESOURCE_FILES)

