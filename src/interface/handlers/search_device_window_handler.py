# Default library imports
from src.database.device_dao import DeviceDao
from src.models.device import Device
import src.utilities.wbb_calitera as wbb
import src.utilities.conexao as conn
from gi.repository import Gtk
from datetime import datetime

# Third party imports
import gi

gi.require_version("Gtk", "3.0")

# Local imports


class Handler:
    def __init__(self, window):
        self.window = window
        self.device_dao = DeviceDao()
        self.device_list = self.device_dao.list_devices()

    def on_show(self, window):
        """
        This method handles the 'show' signal

        Parameters
        ----------
        window : Gtk.Window
                The window
        """
        # Changing sensitivity
        self.window.combo_box.set_sensitive(False)
        self.window.save_button.set_sensitive(False)
        self.window.connect_button.set_sensitive(False)

        # Clearing combo_box
        self.window.combo_box.remove_all()

    def get_device_data(self):
        """
        This method gets active device_data at combo_box
        """

        device_data = self.window.combo_box.get_active_text()
        name, mac = "", ""
        if device_data:
            name, mac = device_data.split("\n")
            name = name.replace("Nome: ", "")
            mac = mac.replace("MAC: ", "")

        return name, mac

    def on_combo_box_changed(self, combobox):
        """
        This method handles the event of changing combo_box

        Parameters
        ----------
        combobox : Gtk.ComboBoxText
                The combobox
        """
        pass

    def on_cancel_clicked(self, button):
        """
        This method handles the event of clicking cancel button

        Parameters
        ----------
        button : Gtk.Button
                The button
        """
        self.window.hide()

    def get_calibrations(self):
        """
        This method get device calibrations
        """
        calibration = self.window.app.wiimote.get_balance_cal()

        named_calibration = dict()
        for i, sensor in enumerate(
            ["right_top", "right_bottom", "left_top", "left_bottom"]
        ):
            named_calibration[sensor] = calibration[i]

        return named_calibration

    def on_connect_clicked(self, button):
        """
        This method handles the event of clicking connect button

        Parameters
        ----------
        button : Gtk.Button
                The button
        """
        name, mac = self.get_device_data()
        if name and mac:
            self.window.app.wiimote = wbb.conecta(mac)
            # self.window.app.wiimote.led = 1
            self.window.app.connection_flags["device"] = True
            for device in self.device_list:
                if device.mac == mac:
                    self.window.app.device = device
                    break
            else:
                self.window.app.device = Device(
                    name=name,
                    mac=mac,
                    calibrations=self.get_calibrations(),
                    is_default=False,
                    calibration_date=datetime.now(),
                )

            # self.window.app.main_window.edit_device.set_sensitive(True)
            # self.window.app.main_window.calibrate_device.set_sensitive(True)
            self.window.app.main_window.disconnect_device.set_sensitive(True)
            self.window.app.on_verify_connection()
            self.window.app.statusbar.set_text(
                "Dispositivo conectado. ALERTA! Um dispositivo não calibrado gera dados equivocados. Calibre-o assim que possível!"
            )
            self.window.hide()

    def on_search_clicked(self, button):
        """
        This method handles the event of clicking search button

        Parameters
        ----------
        button : Gtk.Button
                The button
        """

        # Starting spinner
        self.window.spinner.start()

        # Changing sensitivity
        self.window.combo_box.set_sensitive(False)
        self.window.save_button.set_sensitive(False)
        self.window.connect_button.set_sensitive(False)

        # Clearing combo_box
        self.window.combo_box.remove_all()

        # Found devices list
        devices = conn.searchWBB()

        # Checking if there is any device in list
        if devices:
            # Filling combo_box
            for device in devices:
                txt = "Nome: {}\nMAC: {}".format(device[1], device[0])
                self.window.combo_box.append_text(txt)

            # Changing sensitivity
            self.window.combo_box.set_sensitive(True)
            self.window.save_button.set_sensitive(True)
            self.window.connect_button.set_sensitive(True)

        # Starting spinner
        self.window.spinner.stop()

    def on_save_clicked(self, button):
        """
        This method handles the event of clicking save button

        Parameters
        ----------
        button : Gtk.Button
                The button
        """

        name, mac = self.get_device_data()
        if name and mac:
            self.window.save_window.device_name.set_text(name)
            self.window.save_window.device_mac.set_text(mac)
            self.window.save_window.show()
