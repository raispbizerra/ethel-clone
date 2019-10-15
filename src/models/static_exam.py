class StaticExam():
	'''
	This class represents a device.

	Attributes
	----------
	sta_ex_cod	: int
		Exam's code at the database; 
	sta_ex_aps	: list
		Exam's anteroposterior mensuration;
	sta_ex_mls	: list
		Exam's mediolateral mensuration;
	sta_ex_date : datetime
		Exam's date;
	sta_ex_pat_cod : int
		Exam's patient code;
	sta_ex_usr_cod : int
		Exam's user code;
	sta_ex_type : str
		Exam's type.
	'''
	def __init__(self, sta_ex_cod = None, sta_ex_aps = None, sta_ex_mls = None, sta_ex_date = None, sta_ex_type = None, sta_ex_pat_cod = None, sta_ex_usr_cod = None):
		self.__cod		= sta_ex_cod
		self.__aps		= sta_ex_aps
		self.__mls		= sta_ex_mls
		self.__date		= sta_ex_date
		self.__type		= sta_ex_type
		self.__pat_cod	= sta_ex_pat_cod
		self.__usr_cod	= sta_ex_usr_cod

	# Getters and Setters
	def get_cod(self):
		return self.__cod

	def set_cod(self, value):
		self.__cod = value

	def get_aps(self):
		return self.__aps

	def set_aps(self, value):
		self.__aps = value

	def get_mls(self):
		return self.__mls

	def set_mls(self, value):
		self.__mls = value

	def get_date(self):
		return self.__date

	def set_date(self, value):
		self.__date = value

	def get_type(self):
		return self.__type

	def set_type(self, value):
		self.__type = value

	def get_pat_cod(self):
		return self.__pat_cod

	def set_pat_cod(self, value):
		self.__pat_cod = value

	def get_usr_cod(self):
		return self.__usr_cod

	def set_usr_cod(self, value):
		self.__usr_cod = value

	def get_exam(self):
		return [self.get_cod(), self.get_aps(), self.get_mls(), self.get_date(), self.get_type(), self.get_pat_cod(), self.get_usr_cod()]

	# Simple printing
	def show(self):
		print("{} {} {} {} {} {} {}".format(self.get_cod(), self.get_aps(), self.get_mls(), self.get_date(), self.get_type(), self.get_pat_cod(), self.get_usr_cod()))
	
	# Comparison methods 
	def __eq__(self, other):
		return self.__cod == other.get_cod() and self.__aps == other.get_aps() and self.__mls == other.get_mls() and self.__pat_cod == other.get_pat_cod() and self.__usr_cod == other.get_usr_cod() and self.__date == other.get_date() and self.__type == other.get_type()

	def __ne__(self, other):
		return self.__cod != other.get_cod() or self.__aps != other.get_aps() or self.__mls != other.get_mls() or self.__pat_cod != other.get_pat_cod() or self.__usr_cod != other.get_usr_cod() or self.__date != other.get_date() or self.__type != other.get_type()