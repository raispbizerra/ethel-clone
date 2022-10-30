# Third party imports
from src.interface.handlers.los_window_handler import Handler
from src.interface.builder import Builder
from gi.repository import Gtk, Gdk
import gi
gi.require_version('Gtk', '3.0')

# Local imports


class LosWindow(Gtk.ApplicationWindow):
    """This class implements Los Window
    """

    def __init__(self, app):
        # Init Gtk.Window class
        super(LosWindow, self).__init__(
            title='Limits of Stability', application=app)
        self.set_modal(True)
        self.set_decorated(False)
        # self.set_resizable(False)
        # self.set_position(Gtk.WindowPosition.CENTER)
        self.set_icon_from_file('media/logo_small.png')
        self.app = app
        self.set_transient_for(self.app.main_window)

        # Assign builder
        builder = Builder('src/interface/glade/exam_window.glade')

        # Get glade objects
        self.box = builder.get_object('box')
        self.drawing_area = builder.get_object('drawing_area')
        self.add(self.box)

        # # Assign handler
        handler = Handler(self)
        builder.connect_signals(handler)

        # Connect signals
        # self.connect('delete-event', self.app.on_delete_event)
        self.connect('delete-event', handler.on_delete_event)
        self.connect('show', handler.on_show)

        self.fullscreen()
