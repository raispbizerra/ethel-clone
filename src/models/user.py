class User():
	'''
	This class represents a user

	Attributes
	----------
	usr_cod : int
		User's code at the database
	usr_name : str
		User's name
	usr_username : str
		User's username
	usr_password : str
		User's password
	usr_email : str
		User's email
	usr_is_adm : bool
		User's is_adm
	'''

	def __init__(self, usr_cod = None, usr_name = None, usr_username = None, usr_password = None, usr_email = None, usr_is_adm = None):
		self.__cod		=  usr_cod
		self.__name		=  usr_name
		self.__username	=  usr_username
		self.__password	=  usr_password
		self.__email	=  usr_email
		self.__is_adm	=  usr_is_adm
	
	# Getters and Setters
	def get_cod(self):
		return self.__cod

	def set_cod(self, value):
		self.__cod = value

	def get_name(self):
		return self.__name

	def set_name(self, value):
		self.__name = value

	def get_username(self):
		return self.__username

	def set_username(self, value):
		self.__username = value

	def get_password(self):
		return self.__password

	def set_password(self, value):
		self.__password = value

	def get_email(self):
		return self.__email

	def set_email(self, value):
		self.__email = value

	def get_is_adm(self):
		return self.__is_adm

	def set_is_adm(self, value):
		self.__is_adm = value

	# Simple printing
	def show(self):
		print("{} {} {} {} {} {}".format(self.get_cod(), self.get_name(), self.get_username(), self.get_password(), self.get_email(), self.get_is_adm()))
	
	# Comparison methods 
	def __eq__(self, other):
		return self.get_cod() == other.get_cod() and self.get_name() == other.get_name() and self.get_username() == other.get_username() and self.get_password() == other.get_password() and self.get_email() == other.get_email() and self.get_is_adm() == other.get_is_adm()

	def __ne__(self, other):
		return self.get_cod() != other.get_cod() or self.get_name() != other.get_name() or self.get_username() != other.get_username() or self.get_password() != other.get_password() or self.get_email() != other.get_email() or self.get_is_adm() != other.get_is_adm()