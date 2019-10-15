class Patient():
	'''
	This class represents a patient

	Attributes
	----------
	pat_cod : int
		Patient's code at the database 
	pat_name : str
		Patient's name
	pat_sex : str
		Patient's sex
	pat_birth : date
		Patient's birth
	pat_height : float
		Patient's height
	pat_weight : float
		Patient's weight
	pat_imc : float
		Patient's imc
	'''

	def __init__(self, pat_cod = None, pat_name = None, pat_sex = None, pat_birth = None, pat_height = None, pat_weight = None, pat_imc = None):
		self.__cod		=	pat_cod
		self.__name		=	pat_name
		self.__sex		=	pat_sex
		self.__birth	=	pat_birth
		self.__height	=	pat_height
		self.__weight	=	pat_weight
		self.__imc		=	pat_imc
	
	# Getters and Setters
	def get_cod(self):
		return self.__cod

	def set_cod(self, value):
		self.__cod = value

	def get_name(self):
		return self.__name

	def set_name(self, value):
		self.__name = value

	def get_sex(self):
		return self.__sex

	def set_sex(self, value):
		self.__sex = value

	def get_birth(self):
		return self.__birth

	def set_birth(self, value):
		self.__birth = value

	def get_height(self):
		return self.__height

	def set_height(self, value):
		self.__height = value

	def get_weight(self):
		return self.__weight

	def set_weight(self, value):
		self.__weight = value

	def get_imc(self):
		return self.__imc

	def set_imc(self, value):
		self.__imc = value

	def get_patient(self):
		return [self.get_cod(), self.get_name(), self.get_sex(), self.get_birth(), self.get_height(), self.get_weight(), self.get_imc()]

	# Simple printing
	def show(self):
		return ("Nome: {}\nSexo: {}\nNascimento: {}\nAltura (cm): {}\nPeso (kg): {}\nIMC: {}".format(self.get_name(), self.get_sex(), self.get_birth(), self.get_height(), self.get_weight(), self.get_imc()))
	
	# Comparison methods 
	def __eq__(self, other):
		return self.get_cod() == other.get_cod() and self.get_name() == other.get_name() and self.get_sex() == other.get_sex() and self.get_birth() == other.get_birth() and self.get_height() == other.get_height() and self.get_weight() == other.get_weight() and self.get_imc() == other.get_imc()

	def __ne__(self, other):
		return self.get_cod() != other.get_cod() or self.get_name() != other.get_name() or self.get_sex() != other.get_sex() or self.get_birth() != other.get_birth() or self.get_height() != other.get_height() or self.get_weight() != other.get_weight() or self.get_imc() != other.get_imc()