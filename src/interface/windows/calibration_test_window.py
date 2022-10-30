# Third party imports
from src.interface.handlers.calibration_test_window_handler import Handler
from src.interface.builder import Builder
from gi.repository import Gtk, Gdk
import gi
gi.require_version('Gtk', '3.0')

# Local imports


class CalibrationTestWindow(Gtk.ApplicationWindow):
    """This class implements Calibration Test Window
    """

    def __init__(self, app):
        # Init Gtk.Window class
        super(CalibrationTestWindow, self).__init__(
            title='Calibration Test', application=app)
        self.set_modal(True)
        self.set_decorated(False)
        # self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_icon_from_file('media/logo_small.png')
        self.app = app
        self.set_transient_for(self.app.calibration_window)

        # Assign builder
        builder = Builder('src/interface/glade/calibration_test_window.glade')

        # Get glade objects
        box = builder.get_object('box')
        self.drawing_area = builder.get_object('drawing_area')
        self.reset_button = builder.get_object('reset_button')
        self.add(box)

        # # Assign handler
        handler = Handler(self)
        builder.connect_signals(handler)

        # Connect signals
        # self.connect('delete-event', self.app.on_delete_event)
        self.connect('delete-event', handler.on_delete_event)
        self.connect('show', handler.on_show)
