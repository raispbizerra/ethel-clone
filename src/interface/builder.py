from gi.repository import Gtk
import gi
gi.require_version('Gtk', '3.0')


class Builder(Gtk.Builder):
    def __init__(self, file):
        Gtk.Builder.__init__(self)

        self.file = file
        self.add_from_file(self.file)
