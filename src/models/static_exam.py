class StaticExam():
    '''
    This class represents a static exam .

    Attributes
    ----------
    cod : int
        Exam's code at the database; 
    aps : list
        Exam's anteroposterior mensuration;
    mls : list
        Exam's mediolateral mensuration;
    date : datetime
        Exam's date;
    pat_cod : int
        Exam's patient code;
    usr_cod : int
        Exam's user code;
    state : str
        Exam's state.
    '''
    def __init__(self, cod = None, aps = None, mls = None, date = None, state = None, pat_cod = None, usr_cod = None):
        self._cod       = cod
        self._aps       = aps
        self._mls       = mls
        self._date      = date
        self._state     = state
        self._pat_cod   = pat_cod
        self._usr_cod   = usr_cod

    @property
    def cod(self):
        return self._cod

    @cod.setter
    def cod(self, cod):
        self._cod = cod

    @property
    def aps(self):
        return self._aps

    @aps.setter
    def aps(self, aps):
        self._aps = aps

    @property
    def mls(self):
        return self._mls

    @mls.setter
    def mls(self, mls):
        self._mls = mls

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, date):
        self._date = date

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        self._state = state

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