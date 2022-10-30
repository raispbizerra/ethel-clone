# Third party imports
from src.database.device_dao import DeviceDao
from src.models.device import Device
from bluetooth.btcommon import is_valid_address as iva
from gi.repository import Gtk
import gi

gi.require_version("Gtk", "3.0")

# Local imports


class Handler:
    """This class implements Device Window Handler"""

    def __init__(self, window):
        self.window = window
        self.device_dao = DeviceDao()

    def get_default(self, is_default):
        """
        This method changes is_default button
        """
        self.window.is_default.set_active(bool(is_default))

    def on_show(self, window):
        """
        This method handles show event
        """
        # Device list
        self.device_list = self.device_dao.list_devices()

        # Check if is modifying
        if self.window.app.change_flags["device"]:
            data = [
                self.window.app.device.name,
                self.window.app.device.mac,
                self.window.app.device.is_default,
                self.window.app.device.calibrations,
                self.window.app.device.calibration_date,
            ]
            self.get_default(data[3])
            data.remove(data[2])
            for i, entry in enumerate(
                [self.window.device_name, self.window.device_mac]
            ):
                entry.set_text(str(data[i]))

    def clear_window(self):
        """
        This method clears the window
        """
        self.window.device_name.set_text("")
        self.window.device_mac.set_text("")
        self.window.is_default.set_active(False)

    def on_cancel_clicked(self, button):
        """
        This method handles the event of click cancel button

        Parameters
        ----------
        button : Gtk.Button
                The button
        """
        self.clear_window()
        self.window.hide()

    def on_save_clicked(self, button):
        """
        This method handles the event of click add button

        Parameters
        ----------
        button : Gtk.Button
                The button

        Returns
        -------
        None or Device
                Whether the operation was succesful
        """
        # Get entries
        name = self.window.device_name.get_text().upper()
        mac = self.window.device_mac.get_text().upper()
        is_default = int(self.window.is_default.get_active())

        # Test if values are valid
        if name == "" or not iva(mac):
            print("Dados inválidos!")
            return None

        # Set all devices to not default
        if is_default:
            self.device_dao.set_all_not_default()

        if self.window.app.change_flags["device"]:
            # Update device
            self.window.app.device.name = name
            self.window.app.device.mac = mac
            self.window.app.device.is_default = is_default
            self.device_dao.update_device(self.window.app.device)
            # Show status
            self.window.app.statusbar.set_text("Dispositivo salvo.")
        else:
            for dev in self.device_list:
                if dev.mac == mac:
                    self.window.statusbar.set_text("Dispositivo já existente!")
                    return
            device = Device(name=name, mac=mac, is_default=is_default)
            # Create device
            self.device_dao.create_device(device)
            # Show status
            self.window.app.statusbar.set_text(
                "Dispositivo salvo. ALERTA! Um dispositivo não calibrado gera dados equivocados. Calibre-o assim que possível."
            )

        # Clear and close window
        self.clear_window()
        self.window.hide()
