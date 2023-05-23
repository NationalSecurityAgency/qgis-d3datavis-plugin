PLUGINNAME = d3datavis
PLUGINS = "$(HOME)"/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/$(PLUGINNAME)
PY_FILES = __init__.py d3datavis.py filewordcloud.py genwordcloud.py heatmapDialog.py provider.py
EXTRAS = metadata.txt
D3 = d3/d3.min.js d3/circularHeatChart.js

deploy:
	mkdir -p $(PLUGINS)
	cp -vf $(PY_FILES) $(PLUGINS)
	cp -vf $(EXTRAS) $(PLUGINS)
	cp -vfr ui $(PLUGINS)
	cp -vfr templates $(PLUGINS)
	mkdir -p $(PLUGINS)/d3/
	cp -vf $(D3) $(PLUGINS)/d3/
	cp -vfr help $(PLUGINS)
	cp -vfr icons $(PLUGINS)
	cp -vf helphead.html index.html
	python -m markdown -x extra readme.md >> index.html
	echo '</body>' >> index.html
	cp -vf index.html $(PLUGINS)/index.html
