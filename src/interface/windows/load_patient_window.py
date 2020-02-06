# Third party imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

# Local imports
from src.interface.builder import Builder
from src.interface.handlers.load_patient_window_handler import Handler
from src.models.patient import Patient

class LoadPatientWindow(Gtk.ApplicationWindow):
    """This class implements Load Patient Window
    """

    def __init__(self, app):
        # Init Gtk.Window class
        super(LoadPatientWindow, self).__init__(title='Carregar paciente', application=app)
        self.set_modal(True)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.set_icon_from_file('media/logo_small.png')
        self.app = app
        self.set_transient_for(self.app.main_window)
        
        # Assign builder
        builder = Builder('src/interface/glade/load_patient_window.glade')

        # Gett glade objects
        box = builder.get_object('box')
        self.search = builder.get_object('search')
        self.treeview = builder.get_object('treeview')
        self.liststore = builder.get_object('liststore')
        self.load_button = builder.get_object('load_button')
        self.add(box)

        # Assign handler
        self.handler = Handler(self)
        builder.connect_signals(self.handler)

        # Connect signals
        self.connect('show', self.handler.on_show)
        self.connect('delete-event', self.app.on_delete_event)