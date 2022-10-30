# Third party imports
from src.interface.handlers.patient_window_handler import Handler
from src.interface.builder import Builder
from gi.repository import Gtk, Gdk
import gi

gi.require_version("Gtk", "3.0")

# Local imports


class PatientWindow(Gtk.ApplicationWindow):
    """This class implements Patient Window"""

    def __init__(self, app):
        # Init Gtk.Window class
        super(PatientWindow, self).__init__(title="Dados do paciente", application=app)
        self.set_modal(True)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_icon_from_file("media/logo_small.png")
        self.app = app
        self.set_transient_for(self.app.main_window)

        # Assigning builder
        builder = Builder("src/interface/glade/patient_window1.glade")

        # Getting glade objects
        box = builder.get_object("box")
        self.popover = builder.get_object("popover")
        self.calendar = builder.get_object("calendar")
        self.name = builder.get_object("name")
        self.birth = builder.get_object("birth")
        self.sex = builder.get_object("sex")
        self.height = builder.get_object("height")
        self.weight = builder.get_object("weight")
        self.imc = builder.get_object("imc")
        self.statusbar = builder.get_object("statusbar")
        self.combobox_month = builder.get_object("combobox_month")
        self.spin_year = builder.get_object("spin_year")
        self.add(box)

        # Assign handler
        handler = Handler(self)
        builder.connect_signals(handler)

        # Connect signals
        self.connect("delete-event", self.app.on_delete_event)
        self.connect("show", handler.on_show)
