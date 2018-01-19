PLUGINNAME = d3datavis
PLUGINS = $(HOME)/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/$(PLUGINNAME)
PY_FILES = d3datavis.py __init__.py heatmapDialog.py
EXTRAS = icon.png metadata.txt
UI_FILES = heatmapdialog.ui
TEMPLATES = templates/index.html
D3 = d3/d3.min.js d3/circularHeatChart.js

deploy:
	mkdir -p $(PLUGINS)
	cp -vf $(PY_FILES) $(PLUGINS)
	cp -vf $(UI_FILES) $(PLUGINS)
	cp -vf $(EXTRAS) $(PLUGINS)
	mkdir -p $(PLUGINS)/templates/
	cp -vf $(TEMPLATES) $(PLUGINS)/templates/
	mkdir -p $(PLUGINS)/d3/
	cp -vf $(D3) $(PLUGINS)/d3/
	cp -vfr help $(PLUGINS)
	cp -vf helphead.html $(PLUGINS)/index.html
	python -m markdown -x markdown.extensions.headerid README.md >> $(PLUGINS)/index.html
	echo '</body>' >> $(PLUGINS)/index.html

