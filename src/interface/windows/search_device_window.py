# Third party imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

# Local imports
from src.interface.builder import Builder
from src.interface.handlers.search_device_window_handler import Handler

class SearchDeviceWindow(Gtk.ApplicationWindow):
    """This class implements search device window
    """

    def __init__(self, app):
        # Init Gtk.Window class
        super(SearchDeviceWindow, self).__init__(title='Buscar dispositivo', application=app)
        self.set_modal(True)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_icon_from_file('media/logo_small.png')
        self.app = app
        self.set_transient_for(self.app.main_window)
        
        # Assign builder
        builder = Builder('src/interface/glade/search_device_window.glade')

        # Get glade objects
        box = builder.get_object('box')
        self.combo_box = builder.get_object('combo_box')
        self.save_button = builder.get_object('save_button')
        self.connect_button = builder.get_object('connect_button')
        self.spinner = builder.get_object('spinner')
        self.add(box)

        # Assign handler
        handler = Handler(self)
        builder.connect_signals(handler)

        # Connect signals
        self.connect('delete-event', self.app.on_delete_event)
        self.connect('show', handler.on_show)

        # Get save_window
        self.save_window = self.app.device_window