#!/usr/bin/env python

import IPython.core.display
import json

class Retina:
    def __init__(self, action='none', debug=False):
        self.action = action
        self.debug  = debug
        self.rcss   = [ 'http://raw.github.com/MG-RAST/Retina/master/css/bootstrap.min.css' ]
        self.rlibs  = [ 'http://raw.github.com/MG-RAST/Retina/master/js/bootstrap.min.js',
                        'http://raw.github.com/MG-RAST/Retina/master/js/retina.js' ,
                        'http://raw.github.com/MG-RAST/Retina/master/js/stm.js',
                        'http://raw.github.com/MG-RAST/Retina/master/js/ipy.js' ]
        self.renderer_resource = "http://raw.github.com/MG-RAST/Retina/master/renderers/";
        src = """
			(function(){
				Retina.init( { library_resource: "http://raw.github.com/MG-RAST/Retina/master/js/" });
			})();
		"""
        IPython.core.display.display_javascript(IPython.core.display.Javascript(data=src, lib=self.rlibs, css=self.rcss))
    
    def graph(self, width=800, height=400, btype="column", target="target", data=None, title="", x_labels="[' ']", x_title="", y_title="", show_legend=False, legend_position='left', title_color="black", x_title_color="black", y_title_color="black", x_labels_rotation="0", x_tick_interval=0, y_tick_interval=30, x_labeled_tick_interval=1, y_labeled_tick_interval=5, default_line_color="black", default_line_width=1, chartArea=None, legendArea=None, onclick="clickedCell"):
	"""Graph Renderer
  
  Displays a graph of pie / bar charts with an optional legend.
  
  Options
  
  btype (STRING)
      Defines the display type of the graph, can be one of
        pie
        column
        stackedColumn
        row
        stackedRow
        line
      Default is column.
  
  title (STRING)
      Title string written at the top of the graph
  
  title_color (CSS Color Value)
      Color of the title text. Default is black.
  
  x_title (STRING)
      Title written below the x-axis.
  
  y_title (STRING)
      Title written to the left of the y-axis.
  
  x_title_color (CSS Color Value)
      Color of the x-axis title string. Default is black.
  
  y_title_color (CSS Color Value)
      Color of the y-axis title string. Default is black.
  
  x_labels (ARRAY of STRING)
      List of the labels at the ticks of the x-axis.
  
  x_labels_rotation (STRING)
      A string representing the number of degrees to rotate the labels on the x-axis. Default is 0.
  
  y_labels (ARRAY of STRING)
      List of the labels at the ticks of the y-axis. If no list is passed will use the y-valus.
  
  x_tick_interval (INT)
      Determines how many ticks are actually drawn on the x-axis. Default is 0.
  
  y_tick_interval (INT)
      Determines how many ticks are actually drawn on the y-axis. Default is 30.
  
  x_labeled_tick_interval (INT)
      Determines which ticks on the x-axis get labels. Default is 1.
  
  y_labeled_tick_interval (INT)
      The number of y-axis ticks that get labels. Default is 5.
  
  default_line_color (CSS Color Value)
      Determines the color of lines if not specified for an individual line. Default is black.
  
  default_line_width (INT)
      Number of pixels lines should be wide if not specified for an individual line. Default is 1.
  
  show_legend (BOOLEAN)
      Turns the display of the legend on / off. Default ist true.
  
  legend_position (STRING)
      Can be one of
        left
        right
        top
        bottom
  
  chartArea (ARRAY of FLOAT)
     The values passed correspond to the left, top, right and bottom margin of the chart area respectively. The position is relative to the top left corner of the containing div. Values less than 1 are interpreted as fractions. Values greater than 1 are interpreted as absolute pixel values.
  
  legendArea (ARRAY of FLOAT)
      If this parameter is set, the legend_position parameter will not be used. Instead pass an array of floats. The values correspond to the left, top, right and bottom margin of the legend area respectively. The position is relative to the top left corner of the containing div. Values less than 1 are interpreted as fractions. Values greater than 1 are interpreted as absolute pixel values.
  
  width (INT)
      The width of the graph in pixel (including legend).
  
  height (INT)
      The height of the graph in pixel (including legend).
  
  data (ARRAY of OBJECT)
      List of data series. Each series has a name and a data attribute. The data attribute is a list of y-values for the series.
  
  onclick (STRING)
      Name of the variable the data of the clicked slice / bar should be written to. Default is clickedCell.
	"""
        html = "<div id='%s'></div>"%(target)
        IPython.core.display.display_html(IPython.core.display.HTML(data=html))
        if data is None:
            title = "Browser Usage"
            x_labels = "['2005','2006','2007','2008']"
            data = "Retina.RendererInstances.graph[0].exampleData()"
        else:
            data = json.dumps(data)

        opt = "width: %d, height: %d, type: '%s', target: document.getElementById('%s'), data: %s, title: '%s', x_labels: %s, x_title: '%s', y_title: '%s', show_legend: %s, legend_position: '%s', title_color: '%s', x_title_color: '%s', y_title_color: '%s', x_labels_rotation: '%s', x_tick_interval: %d, y_tick_interval: %d, x_labeled_tick_interval: %d, y_labeled_tick_interval: %d, default_line_color: '%s', default_line_width: %d"%(width, height, btype, target, data, title, x_labels, x_title, y_title, self._bool(show_legend), legend_position, title_color, x_title_color, y_title_color, x_labels_rotation, x_tick_interval, y_tick_interval, x_labeled_tick_interval, y_labeled_tick_interval, default_line_color, default_line_width)
        
        if chartArea:
            opt += ", chartArea: "+json.dumps(chartArea)
        if legendArea:
            opt += ", legendArea: "+json.dumps(legendArea)
        
        src = """
			(function(){
				Retina.add_renderer({"name": "graph", "resource": '""" + self.renderer_resource + """', "filename": "renderer.graph.js" });
				Retina.load_renderer("graph").then( function () { Retina.Renderer.create('graph', {""" + opt + """, onclick: function(params){ipy.write_cell(ipy.add_cell(), '""" + onclick + """ = '+ JSON.stringify(params));}}).render(); });
                        })();
		"""
        if self.debug:
            print src
        else:
            IPython.core.display.display_javascript(IPython.core.display.Javascript(data=src))
    
    def plot(self, width=800, height=400, target="target", data=None, title="", show_legend=True, legend_position='left'):
        html = "<div id='%s'></div>"%(target)
        IPython.core.display.display_html(IPython.core.display.HTML(data=html))
        if data is None:
            title = "Sine"
            data = "Retina.RendererInstances.plot[0].exampleData()"
        else:
            data = json.dumps(data)
        
        opt = "width: %d, height: %d, target: document.getElementById('%s'), data: %s, title: '%s', show_legend: %s, legend_position: '%s'"%(width, height, target, data, title, self._bool(show_legend), legend_position)
        src = """
			(function(){
				Retina.add_renderer({"name": "plot", "resource": '""" + self.renderer_resource + """', "filename": "renderer.plot.js" });
				Retina.load_renderer("plot").then( function () { Retina.Renderer.create('plot', {""" + opt + """}).render(); });
                        })();
		"""
        if self.debug:
            print src
        else:
            IPython.core.display.display_javascript(IPython.core.display.Javascript(data=src))
    
    def paragraph(self, width="span12", target="target", data=None, title_color='black', header_color='black', text_color='black', raw=False):
        html = "<div id='%s'></div>"%(target)
        IPython.core.display.display_html(IPython.core.display.HTML(data=html))
        if data is None:
            data = "Retina.RendererInstances.paragraph[0].exampleData()"
        else:
            data = json.dumps(data)
        
        opt = "width: '%s', target: document.getElementById('%s'), data: %s, title_color: '%s', header_color: '%s', text_color: '%s', raw: %s"%(width, target, data, title_color, header_color, text_color, self._bool(raw))
        src = """
			(function(){
				Retina.add_renderer({ name: 'paragraph', resource: '""" + self.renderer_resource + """', filename: 'renderer.paragraph.js' });
				Retina.load_renderer('paragraph').then( function () { Retina.Renderer.create('paragraph', {""" + opt + """} ).render(); } );
			})();
		"""
        if self.debug:
            print src
        else:
            IPython.core.display.display_javascript(IPython.core.display.Javascript(data=src))
    
    def _bool(self, aBool):
        if aBool:
            return 'true'
        else:
            return 'false'