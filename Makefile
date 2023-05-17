PLUGINNAME = d3datavis
PLUGINS = "$(HOME)"/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/$(PLUGINNAME)
PY_FILES = __init__.py d3datavis.py heatmapDialog.py genwordcloud.py
EXTRAS = icon.png metadata.txt wordcloud.png
UI_FILES = heatmapdialog.ui wordcloud.ui
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
	cp -vfr font $(PLUGINS)
	cp -vf helphead.html index.html
	python -m markdown -x extra readme.md >> index.html
	echo '</body>' >> index.html
	cp -vf index.html $(PLUGINS)/index.html
