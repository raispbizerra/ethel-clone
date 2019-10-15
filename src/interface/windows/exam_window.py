# Default library imports
import math

# Third party imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib

# Local imports
from src.interface.builder import Builder

class Monitor():
    """docstring for Monitor"""
    def __init__(self, monitor):
        self.width, self.height = monitor.get_geometry().width, monitor.get_geometry().height
        self.x, self.y = monitor.get_geometry().x, monitor.get_geometry().y
        self.mm_size = (monitor.get_width_mm(), monitor.get_height_mm())
        self.center = Position(self.width//2, self.height//2)

    def __str__(self):
        return f"width: {self.width}\nheight: {self.height}\n\nx: {self.x}\ny: {self.y}\n\nmm_size: {self.mm_size}\n\ncenter: {self.center}\n"

class Position():
    """docstring for Position"""
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y

    def __str__(self):
        return f"{self.x}, {self.y}"

class ExamWindow(Gtk.ApplicationWindow):
    """This class implements Los Window
    """

    def __init__(self, app):
        # Init Gtk.Window class
        super(ExamWindow, self).__init__(application=app)
        self.set_modal(True)
        self.set_decorated(False)
        # self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_icon_from_file('media/logo_small.png')
        self.app = app
        self.set_transient_for(self.app.main_window)
        
        self.open_eyes = True

        # Assign builder
        builder = Builder('src/interface/glade/exam_window.glade')
        
        # Get glade objects
        self.box = builder.get_object('box')
        self.drawing_area = builder.get_object('drawing_area')
        self.add(self.box)

        # Connect signals
        self.connect('delete-event', self.on_delete_event)
        self.connect('show', self.on_show)

        self.fullscreen()

    def on_show(self, window):
        self.set_monitor()  
        self.r, self.g, self.b = 1, .75, 0
        self.time = 0
        self.counting = True
        self.drawing_area.connect('draw', self.on_draw)

    def set_monitor(self):
        display = self.get_screen().get_display()
        monitors = list()
        for i in range(display.get_n_monitors()):
            monitors.append(Monitor(display.get_monitor(i)))

        self.monitor = monitors[-1]
        self.move(self.monitor.x, self.monitor.y)
        self.box.set_size_request(self.monitor.height, self.monitor.height)

    def on_draw(self, widget, cr):
        cr.set_source_rgb(0, 0, 0)
        cr.paint()

        if self.open_eyes:
            self.set_title('Static Posturography - Open Eyes')
            cr.arc(self.monitor.center.x, self.monitor.center.y, 25, 0, 2*math.pi)
            cr.set_source_rgb(self.r, self.g, self.b)
            cr.fill()
        else:
            self.set_title('Static Posturography - Closed Eyes')

        if self.counting:
            cr.save()
            cr.scale(5, 5)
            cr.set_source_rgb(1, 1, 1)
            cr.move_to(self.monitor.center.x, self.monitor.center.y)
            cr.show_text(f"{self.time}")
            cr.restore()

    def on_delete_event(self, window, event):
        self.app.wiimote.led = 0
        GLib.source_remove(self.app.main_window.method_id)
        self.hide()
        return True