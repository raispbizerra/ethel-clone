# Default library imports
from datetime import datetime

# Third party imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Local imports
import src.utilities.wbb_calitera as wbb
from src.database.device_dao import DeviceDao

class Handler():

	def __init__(self, window):
		self.window = window
		self.device_dao = DeviceDao()

	def on_show(self, window):
		'''
		This method handles the 'show' signal

		Parameters
		----------
		window : Gtk.Window
			The window
		'''
		self.device_list = self.device_dao.list_devices() # Device list

		# Clear combobox
		self.window.combo_box.remove_all()

		# Change button sensitivity
		if self.device_list:
			self.window.connect_button.set_sensitive(True)
		else:
			self.window.connect_button.set_sensitive(False)

		# Fill combobox
		i = '-1'
		mac = '00:00:00:00:00:00'
		for device in self.device_list:
			self.window.combo_box.insert(device.cod,  str(device.cod), device.name)
			if device.is_default:
				i = str(device.cod)
				mac = device.mac

		# Set active id to the default device
		self.window.combo_box.set_active_id(i)
		self.window.mac.set_text(mac)

	def on_combo_box_changed(self, combobox):
		'''
		This method handles the event of changing combo_box

		Parameters
		----------
		combobox : Gtk.ComboBoxText
			The combobox
		'''
		i = int(self.window.combo_box.get_active_id())
		for dev in self.device_list:
			if dev.cod == i:
				self.window.app.device = dev
		self.window.mac.set_text(self.window.app.device.mac)

	def on_cancel_clicked(self, button):
		'''
		This method handles the event of clicking cancel button

		Parameters
		----------
		button : Gtk.Button
			The button
		'''
		self.window.hide()
		self.window.app.statusbar.set_text('Seleção cancelada')


	def get_calibrations(self):
		'''
		This method get device calibrations
		'''
		cal_date, calibrations = self.device_dao.read_device_calibrations(self.window.app.device.cod)
		if calibrations:
			self.window.app.device.calibrations = calibrations
			self.window.app.device.calibration_date = cal_date
		else:
			print('Não calibrado')
			calibration = self.window.app.wiimote.get_balance_cal()
			named_calibration = {   'right_top'     : calibration[0],
									'right_bottom'  : calibration[1],
									'left_top'      : calibration[2],
									'left_bottom'   : calibration[3]}
			
			self.window.app.device.calibrations = named_calibration
			self.window.app.device.calibration_date = datetime.now()
			self.device_dao.create_device_calibrations(self.window.app.device.cod, self.window.app.device.calibrations, self.window.app.device.calibration_date)

		print(self.window.app.device.calibrations, self.window.app.device.calibration_date)

	def on_connect_clicked(self, button):
		'''
		This method handles the event of clicking connect button

		Parameters
		----------
		button : Gtk.Button
			The button
		Returns
		-------
		None or Device
			Whether the operation was succesful
		'''
		i = int(self.window.combo_box.get_active_id())
		for device in self.device_list:
			if device.cod == i:
				self.window.app.device = self.device_dao.read_device_by_cod(i)
				break

		self.window.app.wiimote = wbb.conecta(self.window.app.device.mac)
		self.get_calibrations()
		self.window.app.connection_flags['device'] = True
		self.window.app.statusbar.set_text('Dispositivo conectado!')
		self.window.app.main_window.edit_device.set_sensitive(True)
		self.window.app.main_window.calibrate_device.set_sensitive(True)
		self.window.app.main_window.disconnect_device.set_sensitive(True)
		self.window.app.on_verify_connection()
		self.window.hide()