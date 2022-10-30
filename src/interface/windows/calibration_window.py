# Third party imports
from src.interface.handlers.calibration_window_handler import Handler
from src.interface.builder import Builder
from gi.repository import Gtk
import gi
gi.require_version('Gtk', '3.0')

# Local imports


class CalibrationWindow(Gtk.ApplicationWindow):
    """This class implements add Device Window
    """

    def __init__(self, app):
        # Init Gtk.Window class
        super(CalibrationWindow, self).__init__(
            title='Calibração', application=app)
        self.set_modal(True)
        self.set_decorated(True)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_icon_from_file('media/logo_small.png')
        self.app = app
        self.set_transient_for(self.app.main_window)

        # Assign builder
        builder = Builder('src/interface/glade/calibration_window.glade')

        # Get glade objects
        self.box = builder.get_object('box')
        # Images
        self.calibration_image = builder.get_object('calibration_image')
        # Buttons
        self.calibration_button = builder.get_object('calibration_button')
        self.test_button = builder.get_object('test_button')
        self.repeat_button = builder.get_object('repeat_button')
        # Labels
        self.calibration_label = builder.get_object('calibration_label')
        self.saved_calibration_date_label = builder.get_object(
            'saved_calibration_date_label')
        self.saved_calibration_label = builder.get_object(
            'saved_calibration_label')
        self.new_calibration_date_label = builder.get_object(
            'new_calibration_date_label')
        self.new_calibration_label = builder.get_object(
            'new_calibration_label')
        # Spins
        self.med_weight_spin = builder.get_object('med_weight_spin')
        self.max_weight_spin = builder.get_object('max_weight_spin')
        # Progress bars
        self.progress_bar = builder.get_object('progress_bar')

        # Add box to window
        self.add(self.box)

        # Assign handler
        self.handler = Handler(self)
        builder.connect_signals(self.handler)

        # Connect signals
        self.connect('delete-event', self.app.on_delete_event)
        self.connect('show', self.handler.on_show)
        self.connect('key-press-event', self.handler.on_key_press_event)
