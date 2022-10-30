class DynamicExam():
    '''
    This class represents a dynamic exam (limits of stability).

    Attributes
    ----------
    cod : int
        Exam's code at the database; 
    cop_x: numpy.array
        Exam's center of pressure x_axis;
    cop_y: numpy.array
        Exam's center of pressure y_axis;
    date : datetime
        Exam's date;
    pat_cod : int
        Exam's patient code;
    usr_cod : int
        Exam's user code;
    '''

    def __init__(self, cod=None, cop_x=None, cop_y=None, date=None, pat_cod=None, usr_cod=None):
        self._cod = cod
        self._cop_x = cop_x
        self._cop_y = cop_y
        self._date = date
        self._pat_cod = pat_cod
        self._usr_cod = usr_cod

    @property
    def cod(self):
        return self._cod

    @cod.setter
    def cod(self, cod):
        self._cod = cod

    @property
    def cop_x(self):
        return self._cop_x

    @cop_x.setter
    def cop_x(self, cop_x):
        self._cop_x = cop_x

    @property
    def cop_y(self):
        return self._cop_y

    @cop_y.setter
    def cop_y(self, cop_y):
        self._cop_y = cop_y

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, date):
        self._date = date

    @property
    def pat_cod(self):
        return self._pat_cod

    @pat_cod.setter
    def pat_cod(self, pat_cod):
        self._pat_cod = pat_cod

    @property
    def usr_cod(self):
        return self._usr_cod

    @usr_cod.setter
    def usr_cod(self, usr_cod):
        self._usr_cod = usr_cod
