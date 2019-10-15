# Local imports
from src.database.connection import Connection
from src.models.device import Device
import src.utilities.utils as Utils


class DeviceDao():
	"""
	This class communicates Ethel's database to create, read and update devices

	Attributes
	----------
	database : str
		Path to the database
	"""

	def __init__(self, database='src/database/ethel.db'):
		self.__c = Connection()
		self.__db = database

	@property
	def c(self):
		return self.__c

	@property
	def db(self):
		return self.__db

	def create_device(self, device: Device):
		'''
		This method creates a new device

		Parameters
		----------
		device : Device
			The device object

		Returns
		-------
		bool
			Whether the operation was successful or not
		'''
		result = False

		sql = 'SELECT COUNT(*)+1 FROM devices'
		sql_ = 'INSERT INTO devices (dev_cod, dev_name, dev_mac, dev_is_default) values (?,?,?,?)'

		try:
			self.c.connect(self.db) 
			cursor = self.c.conn.execute(sql)
			dev_cod = cursor.fetchone()[0]
			device.set_cod(dev_cod)
			self.c.conn.execute(sql_, [device.get_cod(), device.get_name(), device.get_mac(), device.get_is_default()])
			self.c.conn.commit()
			result = True
		except:
			print("Error!")
		finally:
			self.c.close()
		return result

	def create_device_calibrations(self, dev_cod: int, dev_calibrations: dict, calibration_date):
		'''
		This method creates new device calibrations

		Parameters
		----------
		dev_cod : int
			The device code
		dev_calibrations : dict
			The device calibrations
		calibration_date : datetime
			The calibration date

		Returns
		-------
		bool
			Whether the operation was successful or not
		'''
		result = False
		sql = 'INSERT INTO calibrations (cal_right_top, cal_right_bottom, cal_left_top, cal_left_bottom, cal_date, dev_cod) values (?,?,?,?,?,?)'
		cal_right_top, cal_right_bottom, cal_left_top, cal_left_bottom = Utils.dict_to_strs(dev_calibrations)
		cal_date = Utils.datetime_to_str(calibration_date)
		try:
			self.c.connect(self.db)
			self.c.conn.execute(sql, [cal_right_top, cal_right_bottom, cal_left_top, cal_left_bottom, cal_date, dev_cod])
			self.c.conn.commit()
			result = True
		except:
			print("Error!")
		finally:
			self.c.close()
		return result

	def read_device_by_mac(self, dev_mac: str):
		'''
		This method reads an existent Device from Ethel's database.

		Parameters
		----------
		dev_mac : str
			The device mac

		Returns
		-------
		False or Device
			Whether the operation was successful or not
		'''
		device = False
		sql = 'SELECT d.dev_cod, d.dev_name, d.dev_is_default, c.cal_date, c.cal_right_top, c.cal_right_bottom, c.cal_left_top, c.cal_left_bottom FROM devices as d, calibrations as c WHERE d.dev_mac = ? AND d.dev_cod = c.dev_cod'
		try:
			self.c.connect(self.db)
			cursor = self.c.conn.execute(sql, [dev_mac])
			result = cursor.fetchone()
			if result:
				keys = ['right_top', 'right_bottom', 'left_top', 'left_bottom']
				cal_date = Utils.str_to_datetime(result[3])	
				dev_calibrations = Utils.strs_to_dict(keys, result[4:])
				device = Device(result[0], result[1], dev_mac, result[2], dev_calibrations, cal_date)
		except:
			print("Error!")
		finally:
			self.c.close()
		return device

	def read_device_calibrations(self, dev_cod: int):
		'''
		This method reads an existent Device from Ethel's database.

		Parameters
		----------
		dev_cod : int
			The device cod

		Returns
		-------
		False or Device
			Whether the operation was successful or not
		'''
		cal_date, dev_calibrations = None, None
		sql = 'SELECT c.cal_date, c.cal_right_top, c.cal_right_bottom, c.cal_left_top, c.cal_left_bottom FROM calibrations as c WHERE c.dev_cod = ?'
		try:
			self.c.connect(self.db)
			cursor = self.c.conn.execute(sql, [dev_cod])
			result = cursor.fetchone()
			if result:
				keys = ['right_top', 'right_bottom', 'left_top', 'left_bottom']
				cal_date = Utils.str_to_datetime(result[0])	
				dev_calibrations = Utils.strs_to_dict(keys, result[1:])
		except:
			print("Error!")
		finally:
			self.c.close()
		return cal_date, dev_calibrations

	def read_device_by_cod(self, dev_cod: int):
		'''
		This method reads an existent Device from Ethel's database.

		Parameters
		----------
		dev_cod : int
			The device cod

		Returns
		-------
		False or Device
			Whether the operation was successful or not
		'''
		device = Device()
		sql = 'SELECT d.dev_name, d.dev_mac, d.dev_is_default FROM devices as d WHERE d.dev_cod = ?'
		try:
			self.c.connect(self.db)
			cursor = self.c.conn.execute(sql, [dev_cod])
			result = cursor.fetchone()
			if result:
				device = Device(dev_cod, result[0], result[1], result[2])
		except:
			print("Error!")
		finally:
			self.c.close()
		return device

	def update_device(self, device: Device):
		'''
		This method updates an existent Device into Ethel's database.

		Parameters
		----------
		device : Device
			The device object

		Returns
		-------
		bool
			Whether the operation was successful or not
		'''
		result = False
		sql = 'UPDATE devices SET dev_name = ?, dev_mac = ?, dev_is_default = ? WHERE dev_cod = ?'

		try:
			self.c.connect(self.db)
			self.c.conn.execute(sql, [device.get_name(), device.get_mac(), device.get_is_default(), device.get_cod()])
			self.c.conn.commit()
			result = True
		except:
			print("Error!")
		finally:
			self.c.close()
		return result

	def update_device_calibrations(self, dev_cod: int, dev_calibrations: dict, calibration_date):
		'''
		This method updates device calibrations

		Parameters
		----------
		dev_cod : int
			The device code
		dev_calibrations : dict
			The device calibrations

		Returns
		-------
		bool
			Whether the operation was successful or not
		'''
		result = False
		sql = 'UPDATE calibrations SET cal_date = ?, cal_right_top = ?, cal_right_bottom = ?, cal_left_top = ?, cal_left_bottom = ? WHERE dev_cod = ?'
		cal_right_top, cal_right_bottom, cal_left_top, cal_left_bottom = Utils.dict_to_strs(dev_calibrations)
		cal_date = Utils.datetime_to_str(calibration_date)

		try:
			self.c.connect(self.db)
			self.c.conn.execute(sql, [cal_date, cal_right_top, cal_right_bottom, cal_left_top, cal_left_bottom, dev_cod])
			self.c.conn.commit()
			result = True
		except:
			print("Error!")
		finally:
			self.c.close()
		return result

	def list_devices(self):
		'''
		This method lists all devices from Ethel's database.

		Returns
		-------
		bool or list
			Whether the operation was successful or not
		'''
		devices = False
		sql = 'SELECT d.dev_cod, d.dev_name, d.dev_mac, d.dev_is_default FROM devices as d'
		try:
			self.c.connect(self.db)
			cursor = self.c.conn.execute(sql)
			results = cursor.fetchall()
			devices = list()
			for result in results:
				device = Device(result[0], result[1], result[2], result[3])
				devices.append(device)
		except:
			print("Error!")
		finally:
			self.c.close()
		return devices

	def set_all_not_default(self):
		'''
		This method set all devices to not default

		Returns
		-------
		bool or list
			Whether the operation was successful or not
		'''
		result = False
		sql = 'UPDATE devices SET dev_is_default = 0'
		try:
			self.c.connect(self.db)
			self.c.conn.execute(sql)
			self.c.conn.commit()
			result = True
		except:
			print("Error!")
		finally:
			self.c.close()
		return result
