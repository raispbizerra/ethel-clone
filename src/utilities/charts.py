import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTK3Cairo as FigureCanvas
from matplotlib.backends.backend_gtk3 import NavigationToolbar2GTK3 as NavigationToolbar

def canvas(figure):
	return FigureCanvas(figure)

def nav_toolbar(canvas, window):
	return NavigationToolbar(canvas, window)

def fig():
	return Figure(figsize=(1,1))

def axis(figure, projection = None):
	return figure.add_subplot(111, projection=projection)