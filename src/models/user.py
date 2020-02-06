class User():
    '''
    This class represents a user

    Attributes
    ----------
    cod : int
        User's code at the database
    name : str
        User's name
    username : str
        User's username
    password : str
        User's password
    email : str
        User's email
    is_adm : bool
        User's is_adm
    '''
    def __init__(self, cod = None, name = None, username = None, password = None, email = None, is_adm = None):
        self._cod       =  cod
        self._name      =  name
        self._username  =  username
        self._password  =  password
        self._email     =  email
        self._is_adm    =  is_adm
    
    # Getters and Setters
    @property
    def cod(self):
        return self._cod

    @cod.setter
    def cod(self, cod):
        self._cod = cod

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, username):
        self._username = username

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        self._password = password

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, email):
        self._email = email

    @property
    def is_adm(self):
        return self._is_adm

    @is_adm.setter
    def is_adm(self, is_adm):
        self._is_adm = is_adm