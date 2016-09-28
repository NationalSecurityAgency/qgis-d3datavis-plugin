function circularHeatChart() {
	var margin = {top: 20, right: 20, bottom: 20, left: 20},
	innerRadius = 50,
	numSegments = 24,
	segmentHeight = 20,
	myData = undefined,
	nullColor = "lightgray",
	graduatedColors = undefined,
	domain = null,
	legendSettings = {legBlockWidth: 30, legBlockHeight: 25, height: 300, width: 200},
	legDivId = undefined,
	defaultColor = 'red',
	range = ["white", "red"],
	accessor = function(d) {return d;},
	radialLabels = segmentLabels = [];

	function chart(selection) {
		if(legDivId) {
			if(graduatedColors) {
				/*
				 * Creates legend for custom colors
				 */

				var legSvg = d3.select("#"+legDivId).append("svg").attr("id", 'legSVG').attr("height", legendSettings.height).attr("class", "legend");

				var g = legSvg.append("g");

				/*
				 * Create rects for each color and band
				 */
				g.selectAll("rect").data(graduatedColors).enter().append("rect")
					.attr("x", 0)
					.attr("y", function(d, idx) {
						return legendSettings.legBlockHeight*(idx*1);
					})
					.attr("width", legendSettings.legBlockWidth)
					.attr("height", legendSettings.legBlockHeight)
					.attr("fill", function(d, idx) {
						return d.color;
					});
				
					g = legSvg.append("g");
					g.selectAll("text").data(graduatedColors).enter().append("text")
						.attr("x", legendSettings.legBlockWidth+5)
						.attr("class", "label")
						.attr("y", function(d, idx) {
							return (legendSettings.legBlockHeight)*((idx+1)*1)-5;
						})
						.attr("width", legendSettings.legBlockWidth)
						.attr("height", legendSettings.legBlockHeight)
						.text(function(d) {
							return d.minVal + " - " + d.maxVal;
						});

			} else {
				/*
				 * Creates legend gradient for custom colors - can only handle 2 colors right now
				 */

				var legSvg = d3.select("#"+legDivId).append("svg").attr("id", legDivId+'Svg');

				var g = legSvg.append("g");

				/*
				 * Create the gradient to reference
				 */
				var grad = g.append("svg:defs")
					.append("svg:linearGradient")
					.attr("id", legDivId+"Gradient")
					.attr("x1", "0%")
					.attr("y1", "0%")
					.attr("x2", "0%")
					.attr("y2", "100%")
					.attr("spreadMethod", "pad")
					.attr("gradientUnits", "userSpaceOnUse");

				/*
				 * Creates the stop colors of the gradient
				 */
				for(var j=0; j < range.length; j++) {
					grad.append("svg:stop")
						.attr("offset", j)
						.attr("stop-color", range[j])
						.attr("stop-opacity", 1);
				}

				/*
				 * Create rect banner for key of gradients legend
				 */
				var g =legSvg.append("g");
				var rect = g.append("rect")
					.attr("x", 0)
					.attr("y", 0)
					.attr("width", legendSettings.legBlockWidth)
					.attr("height", legendSettings.height-1)
					.style("stroke", "black")
					.style("stroke-width", 1)
					.attr("fill", "url(#"+legDivId+"Gradient"+")");

				var min = d3.min(myData);
				var max = d3.max(myData);
				g = legSvg.append("g");
				var labels = [min, max];
				g.selectAll("text").data(labels).enter().append("text")
					.text(function(d) {
						return d;
					})
					.attr("class", "label")
					.attr("x", legendSettings.legBlockWidth+5)
					.attr("y", function(d, idx) {
                        var bbox = this.getBBox();
						if(idx == 0) {
							return -bbox.y;
						} else {
                            return legendSettings.height - (bbox.height + bbox.y);
						}
					});
			}
		}

		selection.each(function(data) {
			var svg = d3.select(this);

			var offset = innerRadius + Math.ceil(data.length / numSegments) * segmentHeight;
			g = svg.append("g")
				.classed("circular-heat", true)
				.attr("transform", "translate(" + parseInt(margin.left + offset) + "," + parseInt(margin.top + offset) + ")");

			var autoDomain = false;
			if (domain === null) {
				domain = d3.extent(data, accessor);
				autoDomain = true;
			}
			var color = d3.scale.linear().domain(domain).range(range);
			if(autoDomain)
				domain = null;

			g.selectAll("path").data(data)
				.enter().append("path")
				.attr("d", d3.svg.arc().innerRadius(ir).outerRadius(or).startAngle(sa).endAngle(ea))
				.attr("fill", function(d) {
					if(d == null || d == undefined) {
						return nullColor;
					}
					if(graduatedColors) {
						var c = chart.determineGraduatedColor(d);
						if(color) {
							return c;
						} else {
							return color(accessor(d));
						}
					} else {
                        return color(accessor(d));
					}
				});


			// Unique id so that the text path defs are unique - is there a better way to do this?
			var id = d3.selectAll(".circular-heat")[0].length;

			//Radial labels
			var lsa = 0.01; //Label start angle
			var labels = svg.append("g")
				.classed("labels", true)
				.classed("radial", true)
				.attr("transform", "translate(" + parseInt(margin.left + offset) + "," + parseInt(margin.top + offset) + ")");

			labels.selectAll("def")
				.data(radialLabels).enter()
				.append("def")
				.append("path")
				.attr("id", function(d, i) {return "radial-label-path-"+id+"-"+i;})
				.attr("d", function(d, i) {
					var r = innerRadius + ((i + 0.2) * segmentHeight);
					return "m" + r * Math.sin(lsa) + " -" + r * Math.cos(lsa) + 
							" a" + r + " " + r + " 0 1 1 -1 0";
				});

			labels.selectAll("text")
				.data(radialLabels).enter()
				.append("text")
				.append("textPath")
				.attr("xlink:href", function(d, i) {return "#radial-label-path-"+id+"-"+i;})
				.style("font-size", 0.6 * segmentHeight + 'px')
				.text(function(d) {return d;});

			//Segment labels
			var segmentLabelOffset = 2;
			var r = innerRadius + Math.ceil(data.length / numSegments) * segmentHeight + segmentLabelOffset;
			labels = svg.append("g")
				.classed("labels", true)
				.classed("segment", true)
				.attr("transform", "translate(" + parseInt(margin.left + offset) + "," + parseInt(margin.top + offset) + ")");

			labels.append("def")
				.append("path")
				.attr("id", "segment-label-path-"+id)
				.attr("d", "m0 -" + r + " a" + r + " " + r + " 0 1 1 -1 0");

			labels.selectAll("text")
				.data(segmentLabels).enter()
				.append("text")
				.append("textPath")
				.attr("xlink:href", "#segment-label-path-"+id)
				.attr("startOffset", function(d, i) {return i * 100 / numSegments + "%";})
				.text(function(d) {return d;});
		});

	}

	/* Arc functions */
	ir = function(d, i) {
		return innerRadius + Math.floor(i/numSegments) * segmentHeight;
	}
	or = function(d, i) {
		return innerRadius + segmentHeight + Math.floor(i/numSegments) * segmentHeight;
	}
	sa = function(d, i) {
		return (i * 2 * Math.PI) / numSegments;
	}
	ea = function(d, i) {
		return ((i + 1) * 2 * Math.PI) / numSegments;
	}

	/* Configuration getters/setters */
	chart.margin = function(_) {
		if (!arguments.length) return margin;
		margin = _;
		return chart;
	};

	chart.innerRadius = function(_) {
		if (!arguments.length) return innerRadius;
		innerRadius = _;
		return chart;
	};

	chart.numSegments = function(_) {
		if (!arguments.length) return numSegments;
		numSegments = _;
		return chart;
	};

	chart.segmentHeight = function(_) {
		if (!arguments.length) return segmentHeight;
		segmentHeight = _;
		return chart;
	};

	chart.domain = function(_) {
		if (!arguments.length) return domain;
		domain = _;
		return chart;
	};
    
	chart.nullColor = function(_) {
		if (!arguments.length) return nullColor;
		nullColor = _;
		return chart;
	};    

	chart.range = function(_) {
		if (!arguments.length) return range;
		range = _;
		return chart;
	};

	chart.radialLabels = function(_) {
		if (!arguments.length) return radialLabels;
		if (_ == null) _ = [];
		radialLabels = _;
		return chart;
	};

	chart.segmentLabels = function(_) {
		if (!arguments.length) return segmentLabels;
		if (_ == null) _ = [];
		segmentLabels = _;
		return chart;
	};

	chart.accessor = function(_) {
		if (!arguments.length) return accessor;
		accessor = _;
		return chart;
	};

	// 1) Color, 2) Min Value, 3) Max value
	/*
	 * Should be an array of objects each object should contain a min value, max value,
	 * and regb/color name/hex value color code
	 * [{minVal: 0, maxVal: 100, color: }]
	 */

	chart.graduatedColors = function(_) {
		if (!arguments.length) return graduatedColors;
		graduatedColors = _;
		return chart;
	};
	
	chart.legendSettings = function(_) {
		if (!arguments.length) return legendSettings;
		for( var attrname in _) {legendSettings[attrname] = _[attrname]; }
		return chart;
	};
	
	chart.legDivId = function(_) {
		if (!arguments.length) return legDivId;
		legDivId = _;
		return chart;
	};
	
	chart.data = function(_) {
		if (!arguments.length) return myData;
		myData = _;
		return chart;
	};

	chart.determineGraduatedColor = function(d) {
		for(var i = 0; i < graduatedColors.length; i++) {
			var obj = graduatedColors[i];

			if(d >= obj.minVal && d <= obj.maxVal) {
				// If no color is set, gets default color
				if(obj.color) {
					return obj.color;
				} else {
					return defaultColor;
				}
			}
		}
	};

	return chart;
}
