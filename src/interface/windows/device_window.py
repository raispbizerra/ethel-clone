# Third party imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

# Local imports
from src.interface.builder import Builder
from src.interface.handlers.device_window_handler import Handler

class DeviceWindow(Gtk.ApplicationWindow):
    """This class implements add Device Window
    """

    def __init__(self, app):
        # Init Gtk.Window class
        super(DeviceWindow, self).__init__(title='Dispositivo', application=app)
        self.set_modal(True)
        self.set_decorated(True)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_icon_from_file('media/logo_small.png')
        self.app = app
        self.set_transient_for(self.app.main_window)

        # Assign builder
        builder = Builder('src/interface/glade/device_window.glade')
        
        # Get glade objects
        box = builder.get_object('box')
        self.device_name = builder.get_object('device_name')
        self.device_mac = builder.get_object('device_mac')
        self.is_default = builder.get_object('is_default')
        self.statusbar = builder.get_object('statusbar')
        self.add(box)

        # Assign handler
        handler = Handler(self)
        builder.connect_signals(handler)
        
        # Connect signals
        self.connect('delete-event', self.app.on_delete_event)
        self.connect('show', handler.on_show)