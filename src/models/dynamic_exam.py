class DynamicExam():
	'''
	This class represents a dynamic exam (limits of stability).

	Attributes
	----------
	dyn_ex_cod	: int
		Exam's code at the database; 
	dyn_ex_cop_x: numpy.array
		Exam's center of pressure x_axis;
	dyn_ex_cop_y: numpy.array
		Exam's center of pressure y_axis;
	dyn_ex_date : datetime
		Exam's date;
	dyn_ex_pat_cod : int
		Exam's patient code;
	dyn_ex_usr_cod : int
		Exam's user code;
	'''
	def __init__(self, ex_cod = None, ex_cop_x = None, ex_cop_y = None, ex_date = None, ex_pat_cod = None, ex_usr_cod = None):
		self.__cod		= ex_cod
		self.__cop_x	= ex_cop_x
		self.__cop_y	= ex_cop_y
		self.__date		= ex_date
		self.__pat_cod	= ex_pat_cod
		self.__usr_cod	= ex_usr_cod

	# Getters and Setters
	def get_cod(self):
		return self.__cod

	def set_cod(self, value):
		self.__cod = value

	def get_cop_x(self):
		return self.__cop_x

	def set_cop_x(self, value):
		self.__cop_x = value
	
	def get_cop_y(self):
		return self.__cop_y

	def set_cop_y(self, value):
		self.__cop_y = value

	def get_date(self):
		return self.__date

	def set_date(self, value):
		self.__date = value

	def get_pat_cod(self):
		return self.__pat_cod

	def set_pat_cod(self, value):
		self.__pat_cod = value

	def get_usr_cod(self):
		return self.__usr_cod

	def set_usr_cod(self, value):
		self.__usr_cod = value

	def get_exam(self):
		return [self.get_cod(), self.get_cop_x(), self.get_cop_y(), self.get_date(), self.get_pat_cod(), self.get_usr_cod()]

	# Simple printing
	def show(self):
		print("{} {} {} {} {} {}".format(self.get_cod(), self.get_cop_x(), self.get_cop_y(), self.get_date(), self.get_pat_cod(), self.get_usr_cod()))
	
	# Comparison methods 
	def __eq__(self, other):
		return self.__cod == other.get_cod() and self.__cop_x == other.get_cop_x() and self.__cop_y == other.get_cop_y() and self.__pat_cod == other.get_pat_cod() and self.__usr_cod == other.get_usr_cod() and self.__date == other.get_date()

	def __ne__(self, other):
		return self.__cod != other.get_cod() or self.__cop_x != other.get_cop_x() or self.__cop_y != other.get_cop_y() or self.__pat_cod != other.get_pat_cod() or self.__usr_cod != other.get_usr_cod() or self.__date != other.get_date()