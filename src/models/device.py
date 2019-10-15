class Device():
	'''
	This class represents a device

	Attributes
	----------
	dev_cod : int
		Device's code at the database 
	dev_name : str
		Device's name
	dev_mac : str
		Device's MAC address
	dev_calibrations : dict
		Device's calibrations
	dev_is_default : bool
		Flag that identifies which one is the default device
	'''

	def __init__(self, dev_cod = None, dev_name = None, dev_mac = None, dev_is_default = None, dev_calibrations = None, dev_calibration_date = None):
		self.__cod            = dev_cod
		self.__name           = dev_name
		self.__mac            = dev_mac
		self.__is_default     = dev_is_default
		self.__calibrations   = dev_calibrations
		self.__calibration_date   = dev_calibration_date
	
	# Getters and Setters
	def get_cod(self):
		return self.__cod

	def set_cod(self, value):
		self.__cod = value

	def get_name(self):
		return self.__name

	def set_name(self, value):
		self.__name = value

	def get_mac(self):
		return self.__mac

	def set_mac(self, value):
		self.__mac = value

	def get_is_default(self):
		return self.__is_default

	def set_is_default(self, value):
		self.__is_default = value

	def get_calibrations(self):
		return self.__calibrations

	def set_calibrations(self, value):
		self.__calibrations = value

	def get_calibration_date(self):
		return self.__calibration_date

	def set_calibration_date(self, value):
		self.__calibration_date = value

	# Simple printing
	def show(self):
		print("{} {} {} {} {}".format(self.get_cod(), self.get_name(), self.get_mac(), self.get_calibrations(), self.get_is_default()))
	
	def get_device(self):
		return [self.get_cod(), self.get_name(), self.get_mac(), self.get_calibrations(), self.get_is_default()]

	# Comparison methods 
	def __eq__(self, other):
		return self.__cod == other.get_cod() and self.__name == other.get_name() and self.__mac == other.get_mac() and self.__calibrations == other.get_calibrations() and self.__is_default == other.get_is_default()

	def __ne__(self, other):
		return self.__cod != other.get_cod() or self.__name != other.get_name() or self.__mac != other.get_mac() or self.__calibrations != other.get_calibrations() or self.__is_default != other.get_is_default()