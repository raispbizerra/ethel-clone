# Default imports
from datetime import datetime

# Third party imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from bluetooth.btcommon import is_valid_address as iva

# Local imports
from src.models.patient import Patient
from src.database.patient_dao import PatientDao
import src.utilities.utils as utils

class Handler():
    """This class implements Patient Window Handler
    """
    def __init__(self, window):
        self.window = window
        self.patient_dao = PatientDao()

    def on_birth_activate(self, widget):
        print('activated')

    def set_sex(self, sex : str):
        '''
        This method set sex from patient
        '''
        for button in self.window.sex.get_children():
            if button.get_label().upper() == sex:
                button.set_active(True)

    def on_show(self, window : Gtk.Window):
        '''
        This method handles the show event

        Parameters
        ----------
        window : Gtk.Window
            The window
        '''
        # Clear window
        self.clear()

        # Modifying
        if self.window.app.change_flags['patient']:
            data = self.window.app.patient.get_patient()[1:]
            self.set_sex(data[1])
            data[2] = utils.date_to_str(data[2])
            data.remove(data[1])
            for i, entry in enumerate([self.window.name, self.window.birth, self.window.height, self.window.weight, self.window.imc]):
                entry.set_text(str(data[i]))
        # else:
        #     year, month, day = datetime.today().date().year, datetime.today().date().month, datetime.today().date().day
        #     self.window.combobox_month.set_active_id(str(month))
        #     self.window.spin_year.set_value(year)
        #     self.window.spin_year.get_adjustment().set_upper(year)
        #     self.window.calendar.year = int(year)
        #     self.window.calendar.month = int(month-1)
        #     self.window.calendar.day = int(day)

    def on_birth_icon_press(self, entry, icon_pos, event):
        '''
        This method handles birth_entry icon click 

        Parameters
        ----------
        entry : Gtk.Entry
            The entry
        icon_pos : Gtk.EntryIconPosition
            The icon position
        event : Gdk.Event
            The event
        '''
        #Popup the popover
        self.window.popover.popup()

    def on_height_changed(self, entry):
        '''
        This method handles height_entry change

        Parameters
        ----------
        entry : Gtk.Entry
            The entry
        '''
        # Only allows numbers
        text = entry.get_text().strip()
        entry.set_text(''.join([i for i in text if i in '0123456789']))

    def select_date(self, widget):
        '''
        This method handles select date event

        Parameters
        ----------
        widget : Gtk.Widget
            The widget
        '''
        # Getting date from calendar
        y, m, d = self.window.calendar.get_date()
        
        # Formating date to show
        m += 1
        dt = datetime(y, m, d).date()

        # Checking if the date is valid
        if dt > datetime.today().date():
            self.window.statusbar.set_text('Data inválida!')
            return
        
        self.window.statusbar.set_text('')

        # Setting entry text
        self.window.birth.set_text(utils.date_to_str(dt))

        # Hiding popover
        self.window.popover.popdown()

    def on_cancel_calendar_clicked(self, button):
        '''
        This method handles cancel calendar click

        Parameters
        ----------
        button : Gtk.Button
            The button
        '''
        self.window.popover.popdown()

    def get_sex(self):
        '''
        This method gets patient sex by button label
        '''
        for child in self.window.sex.get_children():
            if child.get_active():
                return child.get_label().upper()
        return ''

    def on_save_clicked(self, button):
        '''
        This method handles save click

        Parameters
        ----------
        button : Gtk.Button
            The button
        '''

        # Checking if any value is empty
        label   = 0
        article = 1
        value   = 2
        for data in [('Nome', 'o', self.window.name), ('Data de Nascimento', 'a', self.window.birth), ('Altura', 'a', self.window.height)]:
            if data[value].get_text() == '':
                self.window.statusbar.set_text('{} inválid{}!'.format(data[label], data[article]))
                data[value].grab_focus()
                return

        # Getting values
        name    = self.window.name.get_text().upper()
        birth   = utils.str_to_date(self.window.birth.get_text().upper())
        height  = int(self.window.height.get_text())
        sex     = self.get_sex()
        
        # Clearing statusbar
        self.window.statusbar.set_text('')

        # Checking modifying flag
        if self.window.app.change_flags['patient']:
            # Assigning patient
            self.window.app.patient.set_name(name)
            self.window.app.patient.set_birth(birth)
            self.window.app.patient.set_sex(sex)
            self.window.app.patient.set_height(height)
            # Update patient
            self.patient_dao.update_patient(self.window.app.patient)
            # Assigning patient statusbar
            txt = "Nome: {}\tAltura (cm): {}".format(self.window.app.patient.get_name(), self.window.app.patient.get_height())
            self.window.app.patient_label.set_text(txt)
        else:
            # Create patient
            patient = Patient(pat_name=name, pat_birth=birth, pat_sex=sex, pat_height=height)
            self.patient_dao.create_patient(patient)

        # Assigning statusbar
        self.window.app.statusbar.set_text('Paciente Salvo')

        # Hiding window
        self.clear()
        self.window.hide()

    def clear(self):
        '''
        This method handles clear window
        '''
        for entry in [self.window.name, self.window.birth, self.window.height, self.window.weight, self.window.imc]:
            entry.set_text('')

        self.window.combobox_month.set_active_id(str(self.window.calendar.get_date()[1]+1))
        self.window.sex.get_children()[2].set_active(True)
        self.window.statusbar.set_text('')

    def on_cancel_clicked(self, button):
        '''
        This method handles cancel click

        Parameters
        ----------
        button : Gtk.Button
            The button
        '''
        self.window.hide()

    def on_combobox_month_changed(self, combobox):
        '''
        This method handles combobox_month change

        Parameters
        ----------
        combobox : Gtk.ComboBox
            The combobox
        '''
        month = int(self.window.combobox_month.get_active_id())-1
        year = int(self.window.spin_year.get_value())
        self.window.calendar.select_month(month, year)

    def on_spin_year_value_changed(self, spinbutton):
        '''
        This method handles spin_year change

        Parameters
        ----------
        spinbutton : Gtk.SpinButton
            The spinbutton
        '''
        month = int(self.window.combobox_month.get_active_id())-1
        year = int(self.window.spin_year.get_value())
        self.window.calendar.select_month(month, year)

    def on_birth_button_press_event(self, entry):
        '''
        This method handles birth entry activate

        Parameters
        ----------
        entry : Gtk.Entry
            The entry
        '''
        #Popup the popover
        self.window.popover.popup()
