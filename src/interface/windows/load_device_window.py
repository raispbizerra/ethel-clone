# Third party imports
from src.interface.handlers.load_device_window_handler import Handler
from src.interface.builder import Builder
from gi.repository import Gtk, Gdk
import gi
gi.require_version('Gtk', '3.0')

# Local imports


class LoadDeviceWindow(Gtk.ApplicationWindow):
    """This class implements load Device Window
    """

    def __init__(self, app):
        # Init Gtk.Window class
        super(LoadDeviceWindow, self).__init__(
            title='Selecionar dispositivo salvo', application=app)
        self.set_modal(True)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_icon_from_file('media/logo_small.png')
        self.app = app
        self.set_transient_for(self.app.main_window)

        # Assign builder
        builder = Builder('src/interface/glade/load_device_window.glade')

        # Get glade objects
        box = builder.get_object('box')
        self.combo_box = builder.get_object('combo_box')
        self.mac = builder.get_object('mac')
        self.connect_button = builder.get_object('connect_button')
        self.add(box)

        # Assign handler
        handler = Handler(self)
        builder.connect_signals(handler)

        # Connect signals
        self.connect('show', handler.on_show)
        self.connect('delete-event', self.app.on_delete_event)
